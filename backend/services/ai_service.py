from inference_sdk import InferenceHTTPClient
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

def detect_license_plate(image_path):
    try:
        result = client.run_workflow(
            workspace_name="license-plate-detection-mct72",
            workflow_id="custom-workflow-4",
            images={"image": image_path},
            use_cache=True
        )

        print("Roboflow result:", result)

        # Roboflow returns a list, so take the first element
        if isinstance(result, list) and len(result) > 0:
            first_output = result[0]
            if "predictions" in first_output and "predictions" in first_output["predictions"]:
                predictions = first_output["predictions"]["predictions"]
                return predictions

        # If there is no valid result
        print("No valid prediction.")
        return []

    except Exception as e:
        print("AI detect error:", str(e))
        return []
