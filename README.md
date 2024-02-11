# Adaptive Conversational AI Agents (ACAI)
Chatbots are computer programs that simulate human conversation using machine learning and artificial intelligence. Chatbots have been applied to numerous fields, including customer service, education, and physical and mental health. In the context of mental health, chatbots provide an alternative care solution in the face of barriers such as insufficient supply for the current demand, cost, and lack of convenience.
Mental health chatbots exist in abundance -- around 1000 are available on the App Store today. While many are meritorious, there are a common set of critiques. Existing mental health AI agents often feel scripted, unvaried, and unable to respond to the unique, nuanced concerns of users. Overall, there is a lack of personalization -- a characteristic that is still unique to person-to-person therapy. 
This research aims to improve personalization of chatbots with the addition of contextual bandits, in which different contexts are provided to adaptively improve the care provided to individual users. 

## Quick Start

### Installation
```
pip install -r requirements.txt
```

### Init Sqlite3 database
Run the following command to init a database if you don't have one:
```
flask --app flaskr init-db
```

Then you need to run the following command to create the tables:
```
python app/init_db.py
```

### Create Secret YAML file
1. Go to `app/static/` directory, copy `secret_template.yaml` and rename the new file to `secret.yaml`.
2. Go to [OpenAI API Keys](https://platform.openai.com/api-keys), create a new API key token or using an existing one.
3. Paste the API key to `openai` and `azure_openai`.

### Here you go!
Run the following command to start the Flask server:
```
flask run
```
