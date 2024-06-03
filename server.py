# Server Code
# replace [PROTO_FILE_NAME] with Proto filename
# replace [GRPC_SERVICE_NAME] with the service name (name after service command)
# replace [GRPC_METHOD_NAME] with the method name (name after rpc command)
# replace [GRPC_SERVICE_RETURN_TYPE] with the return type that was declared in a message
import grpc
import pb.timesfm_pb2
import pb.timesfm_pb2_grpc
from concurrent import futures
import numpy as np
import timesfm

class Predict_Metrics(pb.timesfm_pb2_grpc.PredictAgriServicer):
    def __init__(self) -> None:
        super().__init__()
        pass
        self.tfm = timesfm.TimesFm(
            context_len=480,
            horizon_len=30,
            input_patch_len=32,
            output_patch_len=128,
            num_layers=20,
            model_dims=1280,
            backend="cpu",
        )
        self.tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m")
        self.num_requests = 0

    def predict_metric(self, request_iter, context):
        """
        grpc server method that predicts metric for the next three months
        Parameters::
            request_iter: protobuf request with metric values of the prev 5 months
        
         Returns:
            metric data for the last 7 months
        """
        print(f"::Incoming Request #{self.num_requests}::")
        request_hist_values = []
        for request in request_iter:
            request_hist_values.append(request.value)
        
        forecast_input = [
            request_hist_values,
        ]
        frequency_input = [1]


        point_forecast, experimental_quantile_forecast = self.tfm.forecast(
            forecast_input,
            freq=frequency_input,
        )

        print(f"Predictions done| output length: {len(point_forecast[0])}")
        self.num_requests += 1

        for forcast in point_forecast[0]:
            yield pb.timesfm_pb2.future_values(value = forcast)

        


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb.timesfm_pb2_grpc.add_PredictAgriServicer_to_server(
        Predict_Metrics(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("running Server on port:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()