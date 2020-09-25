import os
import argparse
import logging
import datetime
import apache_beam as beam
import tensorflow as tf
from apache_beam.options.pipeline_options import PipelineOptions
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata
from tensorflow_transform.tf_metadata import schema_utils
from tensorflow_transform.tf_metadata import dataset_schema
from tensorflow_transform.beam.tft_beam_io import transform_fn_io
from tensorflow_transform.coders import example_proto_coder



class MapAndFilterErrors(beam.PTransform):
  """Like beam.Map but filters out erros in the map_fn."""

  class _MapAndFilterErrorsDoFn(beam.DoFn):
    """Count the bad examples using a beam metric."""

    def __init__(self, fn):
      self._fn = fn
      # Create a counter to measure number of bad elements.
      self._bad_elements_counter = beam.metrics.Metrics.counter(
          'rating_example', 'bad_elements')

    def process(self, element):
      try:
        yield self._fn(element)
      except Exception:  # pylint: disable=broad-except
        # Catch any exception the above call.
        self._bad_elements_counter.inc(1)

  def __init__(self, fn):
    self._fn = fn

  def expand(self, pcoll):
    return pcoll | beam.ParDo(self._MapAndFilterErrorsDoFn(self._fn))


USER_FEATURE_KEYS = [
                'userid',
                'itemid',
]
RATINGS_FEATURE_KEYS = [
                        'ratings',
]

RAW_DATA_FEATURE_SPEC = dict([(name, tf.io.FixedLenFeature([], tf.int64))
                              for name in USER_FEATURE_KEYS] +
                             [(name, tf.io.FixedLenFeature([], tf.float32))
                              for name in RATINGS_FEATURE_KEYS] )

RAW_DATA_METADATA = dataset_metadata.DatasetMetadata(
    schema_utils.schema_from_feature_spec(RAW_DATA_FEATURE_SPEC))


def transform(argv=None):
  """Main entry point; defines and runs the wordcount pipeline."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      default='gs://coterie-rec/rating.csv',
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      required=True,
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  def to_tfrecord(key_vlist, indexCol):
    (key, vlist) = key_vlist
    return {
        "key": [key],
        "indices": [value[indexCol] for value in vlist],
        "values":  [value["ratings"] for value in vlist]
        }

  def write_count(a, outdir, basename):
        filename = os.path.join(outdir, basename)
        (a 
         | "{}_1".format(basename) >> beam.Map(lambda x: (1, 1)) 
         | "{}_2".format(basename) >> beam.combiners.Count.PerKey()
         | "{}_3".format(basename) >> beam.Map(lambda x: x[1])
         | "{}_write".format(basename) >> beam.io.WriteToText(file_path_prefix=filename, num_shards=1))
        
  def preprocessing_fn(inputs):
    """Preprocess input columns into transformed columns."""
    # Since we are modifying some features and leaving others unchanged, we
    # start by setting `outputs` to a copy of `inputs.
    outputs = inputs.copy()

    # Scale numeric columns to have range [0, 1].
    for key in RATINGS_FEATURE_KEYS:
      outputs[key] = tft.scale_to_0_1(outputs[key])

    for key in USER_FEATURE_KEYS:
      tft.vocabulary(inputs[key], vocab_filename=key)

    return outputs


  with beam.Pipeline(options=PipelineOptions(pipeline_args)) as pipeline:
    with tft_beam.Context(temp_dir='/content/'):
      # Create a coder to read the census data with the schema.  To do this we
      # need to list all columns in order since the schema doesn't specify the
      # order of columns in the csv.
      ordered_columns = [
          'userid', 'itemid', 'ratings',
      ]
      converter = tft.coders.CsvCoder(ordered_columns, RAW_DATA_METADATA.schema)
      raw_data = (
          pipeline
          | 'ReadTrainData' >> beam.io.ReadFromText(known_args.input)
          | 'FixCommasTrainData' >> beam.Map(
               lambda line: line.replace(', ', ','))
          | 'DecodeTrainData' >> MapAndFilterErrors(converter.decode))
          # | 'Print output' >> beam.Map(print))
      raw_dataset = (raw_data, RAW_DATA_METADATA)
      transformed_dataset, transform_fn = (
          raw_dataset | tft_beam.AnalyzeAndTransformDataset(preprocessing_fn))
      transformed_data, transformed_metadata = transformed_dataset
      _ = (transform_fn | "WriteTransformFn" >> transform_fn_io.WriteTransformFn(os.path.join(known_args.output, "transform_fn")))
            # do a group-by to create users_for_item and items_for_user
      users_for_item = (transformed_data 
                              | "map_items" >> beam.Map(lambda x : (x["itemid"], x))
                              | "group_items" >> beam.GroupByKey()
                              | "totfr_items" >> beam.Map(lambda item_userlist : to_tfrecord(item_userlist, "userid")))
      items_for_user = (transformed_data
                              | "map_users" >> beam.Map(lambda x : (x["userid"], x))
                              | "group_users" >> beam.GroupByKey()
                              | "totfr_users" >> beam.Map(lambda item_userlist : to_tfrecord(item_userlist, "itemid")))
      output_schema = {
                "key" : dataset_schema.ColumnSchema(tf.int64, [1], dataset_schema.FixedColumnRepresentation()),
                "indices": dataset_schema.ColumnSchema(tf.int64, [], dataset_schema.ListColumnRepresentation()),
                "values": dataset_schema.ColumnSchema(tf.float32, [], dataset_schema.ListColumnRepresentation())
            }

      _ = users_for_item | "users_for_item" >> beam.io.WriteToTFRecord(
                    os.path.join(known_args.output, "users_for_item"),
                    coder = example_proto_coder.ExampleProtoCoder(
                            dataset_schema.Schema(output_schema)))
      _ = items_for_user | "items_for_user" >> beam.io.WriteToTFRecord(
                    os.path.join(known_args.output, "items_for_user"),
                    coder = example_proto_coder.ExampleProtoCoder(
                            dataset_schema.Schema(output_schema)))
      write_count(users_for_item, known_args.output, "nitems")
      write_count(items_for_user, known_args.output, "nusers")  

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  transform()