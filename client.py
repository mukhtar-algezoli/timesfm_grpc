# Client Code
# replace [PROTO_FILE_NAME] with Proto filename
# replace [GRPC_SERVICE_NAME] with the service name (name after service command)
# replace [GRPC_METHOD_NAME] with the method name (name after rpc command)
# replace [GRPC_SERVICE_input_TYPE] with the input type that was declared in a message
import grpc
import timesfm_pb2_grpc
import timesfm_pb2
def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        print("runing client request")
        stub = timesfm_pb2_grpc.PredictAgriStub(channel)
        # calling function from Server
        # feature = stub.GetDirMeth(test_pb2.point(lang=35, lat=22))
        features = stub.predict_metric(iter([timesfm_pb2.prev_values(value=i) for i in range(4,9)]))
        print("server streaming:")
        outputs = []
        for feature in features:
            print(feature.value)
            outputs.append(feature.value)
        # do something with the returned output
        print(outputs)



if __name__ == "__main__":
    run()