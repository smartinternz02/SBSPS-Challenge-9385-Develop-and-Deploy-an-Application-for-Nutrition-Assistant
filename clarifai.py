from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc


stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

CLARIFAI_API_KEY = "04fe7a95051541789ba44a08eaa5722e"
APPLICATION_ID = "Nutrition_Assistant1"

# Authenticate

image = '/home/bala/Desktop/Images/foodsample.jpeg'

metadata = (("authorization", f"Key {CLARIFAI_API_KEY}"),)

with open(image, "rb") as f:
    file_bytes = f.read()

    request = service_pb2.PostModelOutputsRequest(
        model_id='9504135848be0dd2c39bdab0002f78e9',
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        base64=file_bytes
                    )
                )
            )
        ])
    response = stub.PostModelOutputs(request, metadata=metadata)

    if response.status.code != status_code_pb2.SUCCESS:
        raise Exception("Request failed, status code: " +
                        str(response.status.code))

    for concept in response.outputs[0].data.concepts:
        print('%12s: %.2f' % (concept.name, concept.value))
