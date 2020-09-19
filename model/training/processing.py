import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
 

def create_train_test_set(data):
  users = np.array(data[0])
  items = np.array(data[1])
  unique_users = np.unique(users)
  unique_items = np.unique(items)
  n_users = unique_users.shape[0]
  n_items = unique_items.shape[0]
  max_user = unique_users[-1]
  max_item = unique_items[-1]
  if n_users != max_user or n_items != max_item:
    # make an array of 0-indexed unique user ids corresponding to the dataset
    # stack of user ids
    z = np.zeros(max_user+1, dtype=object)
    z[unique_users] = np.arange(n_users)
    u_r = z[users]

    # make an array of 0-indexed unique item ids corresponding to the dataset
    # stack of item ids
    z = np.zeros(max_item+1, dtype=int)
    z[unique_items] = np.arange(n_items)
    i_r = z[items]

    # construct the ratings set from the three stacks
    np_ratings = np.array(data[2])
    ratings = np.zeros((np_ratings.shape[0], 3), dtype=object)
    ratings[:, 0] = u_r
    ratings[:, 1] = i_r
    ratings[:, 2] = np_ratings
  else:
    ratings = np.array(data)
    # deal with 1-based user indices
    ratings[:, 0] -= 1
    ratings[:, 1] -= 1
    TEST_SET_RATIO = 0.1
    train_sparse, test_sparse = _create_sparse_train_and_test(ratings, n_users,n_items,TEST_SET_RATIO)
    return ratings[:, 0], ratings[:, 1], train_sparse, test_sparse


if __name__ == '__main__':
  options = PipelineOptions()
  input_file = 'gs://coterie-rec/ml-100k/u.data'
  with beam.Pipeline(options=options) as pipeline:
    data = (pipeline | 'ReadData' >> beam.io.ReadFromText(input_file, skip_header_lines=0) # read data with beam
        | 'SplitData' >> beam.Map(lambda x: x.split('\t'))
        | 'FormatToDict' >> beam.Map(lambda x: {"userid": x[0], "itemid": x[1], "ratings": x[2], "timestamp": x[3]}) # format to dict and name columns
        | 'DeleteNullData' >> beam.Filter(lambda x: len(x)> 0)
        | 'SelectWantedColumns' >> beam.Map(lambda x: ','.join([x['userid'], x['itemid'], x['ratings']])) # delete irrelevant columns
        #| 'CreateTrainTestSet' >> beam.Map(create_train_test_set)
        | 'writecsv' >> beam.io.WriteToText('result.csv', header='userid, itemid, ratings')) # write data to csv
