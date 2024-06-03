# Server Code
# replace [PROTO_FILE_NAME] with Proto filename
# replace [GRPC_SERVICE_NAME] with the service name (name after service command)
# replace [GRPC_METHOD_NAME] with the method name (name after rpc command)
# replace [GRPC_SERVICE_RETURN_TYPE] with the return type that was declared in a message
import grpc
import timesfm_pb2
import timesfm_pb2_grpc
from concurrent import futures
import numpy as np
import timesfm

class Predict_Metrics(timesfm_pb2_grpc.PredictAgriServicer):
    def __init__(self) -> None:
        super().__init__()
        pass
        self.tfm = timesfm.TimesFm(
            context_len=480,
            horizon_len=14,
            input_patch_len=32,
            output_patch_len=128,
            num_layers=20,
            model_dims=1280,
            backend="cpu",
        )
        self.tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m")

    def predict_metric(self, request_iter, context):
        forecast_input = []
        for request in request_iter:
            # print(request.value)
            forecast_input.append(request.value)
            # yield timesfm_pb2.future_values(value = request.value)
        
        # print(forecast_input)
        
        # forcasts = self.tfm.forecast(
        #     [np.sin(np.linspace(0, 20, 100))],
        #     freq=1 #Weekly,
        #     )
        # print(forcasts)
        forecast_input = [
            forecast_input,
            # np.sin(np.linspace(0, 20, 200)),
            # np.sin(np.linspace(0, 20, 400)),
        ]
        frequency_input = [1]


        point_forecast, experimental_quantile_forecast = self.tfm.forecast(
            forecast_input,
            freq=frequency_input,
        )

        print(point_forecast)
        for forcast in point_forecast:
            yield timesfm_pb2.future_values(value = forcast)

        


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