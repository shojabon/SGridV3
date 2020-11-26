import boto3

sess = boto3.Session(aws_access_key_id="OFYJ3DMC54YH413KF35U", aws_secret_access_key="7hoGXQfsCNnvHqC3x1sUxRF6kNkT181xCivg13nd")
cli = sess.client('s3', endpoint_url="https://ewr1.vultrobjects.com")

def getFilteredFilenames(file_names):
    if len(file_names) == 0:
        start = ''
    else:
        start = file_names[-1]

    response = cli.list_objects_v2(
        Bucket="testdevbucket",
        StartAfter=start
    )

    if 'Contents' in response:
        file_names = [content['Key'] for content in response['Contents']]
        if 'IsTruncated' in response:
            return getFilteredFilenames(file_names)
    return file_names

print(getFilteredFilenames([""]))