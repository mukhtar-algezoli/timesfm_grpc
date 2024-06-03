# Server Code
# replace [PROTO_FILE_NAME] with Proto filename
# replace [GRPC_SERVICE_NAME] with the service name (name after service command)
# replace [GRPC_METHOD_NAME] with the method name (name after rpc command)
# replace [GRPC_SERVICE_RETURN_TYPE] with the return type that was declared in a message
import grpc
import timesfm_pb2
import timesfm_pb2_grpc
from concurrent import futures
import timesfm

class Predict_Metrics(timesfm_pb2_grpc.PredictAgriServicer):
    def __init__(self) -> None:
        super().__init__()
        pass
        tfm = timesfm.TimesFm(
            context_len=480,
            horizon_len=14,
            input_patch_len=32,
            output_patch_len=128,
            num_layers=20,
            model_dims=1280,
            backend="cpu",
        )
        self.model = tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m")

    def predict_metric(self, request_iter, context):
        hist_values = []
        for request in request_iter:
            print(request.value)
            hist_values.append(request.value)
            yield timesfm_pb2.future_values(value = request.value)
        
        # print(hist_values)
        
        # self.model.forecast(
        #     forecast_input,
        #     freq=frequency_input,)

        


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    timesfm_pb2_grpc.add_PredictAgriServicer_to_server(
        Predict_Metrics(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("running Server on port:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()