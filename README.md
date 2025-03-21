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

__Note__: You'll need to provide your Google Gemini API KEY as an environment variable when running the container.

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output.png)

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output-final.png)

