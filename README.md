# Complete-Travel-Recommendation-System

This application uses Google AI Agentic framework, LangChain, and Streamlit to create personalized travel recommendations based on user preferences.

## Features

- Personalized flight recommendations
- Hotel suggestions based on budget and preferences
- Activity recommendations for your destination
- AI-generated travel itineraries
- Budget optimization

</br>

### Installation

Create a `.env` file to store the `GEMINI_API_KEY=""`

`pip install --no-cache-dir -r requirements.txt`

`streamlit run app.py`

Access the application at http://localhost:8501

</br>

### Containerize Streamlit app

+ Build the image:
`docker image build --no-cache -t travel-planner .`

+ Run the container:
`docker container run -d -p 8501:8501 -e GOOGLE_API_KEY="" travel-planner`

</br>

### Deploying container images to Cloud Run

+ Follow the exposed documentation by accessing the official website: 
https://cloud.google.com/run/docs/deploying

+ Access the GCR webapp here: [Google Cloud Run](https://travel-planner-agent-563547455404.us-central1.run.app/)


</br>

### Deploying to GKE


Before deploying the K8s objects, we assume you have at least a GKE Standard one-node cluster span-up in your development environment.

First, you need to encode the GEMINI_API_KEY using the https://base64encode.org website and then add the encoded string to the secret.yaml file.

Second, you must create a dedicated namespace to deploy the K8s objects.

One by one, the K8s objects are applied to that dedicated namespace.

</br>

+ Run the following commands:

`kubectl apply -f secret.yaml -n <dedicated_ namespace>`


`kubectl apply -f configmap.yaml -n <dedicated_ namespace>`


`kubectl apply -f deployment.yaml -n <dedicated_ namespace>`


`kubectl apply -f service.yaml -n <dedicated_ namespace>`

</br>

Also, an ALB will track the GenAI app externally.
Identify the ALB by using the following command:

kubectl get service -n <dedicated_namespace>

Open a new webpage and insert the [ALB public ip](http://34.88.39.19/).



</br>

__Note__: You'll need to provide your Google Gemini API KEY as an environment variable when running the container.

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output.png)

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output-final.png)

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/gcr.png)

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/alb.png)

</br>

