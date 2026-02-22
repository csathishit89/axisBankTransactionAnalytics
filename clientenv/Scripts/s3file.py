import boto3
s3_client = boto3.client('s3')

s3_client.upload_file(
    Filename=r"D:\Sathish\Guvi_HCL\FinalProject\Certification-Poster-en-us.pdf",
    Bucket='axis-bank-pdf-bucket',
    Key='statement-pdf/Certification-Poster-en-us.pdf'
)

s3_client.download_file(
    Filename=r"D:\Sathish\Guvi_HCL\FinalProject\Certification-Poster-en-us.pdf",
    Bucket='axis-bank-pdf-bucket',
    Key='statement-pdf/Certification-Poster-en-us.pdf'
)

s3_client.delete_object(
    Bucket='axis-bank-pdf-bucket',
    Key='statement-pdf/Certification-Poster-en-us.pdf'
)

response = s3_client.list_objects_v2(Bucket='axis-bank-pdf-bucket',Prefix='statement-pdf/')

for object in response.get('Contents', []):
    print(object['Key'], object['Size'])
