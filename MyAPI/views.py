import time
start = time.time()
from django.shortcuts import render
from . forms import MyForm
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.core import serializers
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from . models import predictions
from . serializers import predictionsSerializers
import pickle
from sklearn.externals import joblib
import json
import numpy as np
from sklearn import preprocessing
import pandas as pd
from keras.preprocessing import sequence 
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from twitter_scraper import get_tweets
import re
import string

class ApprovalsView(viewsets.ModelViewSet):
	queryset = predictions.objects.all()
	serializer_class = predictionsSerializers
def clean_text(text):
  regexp = r'pic\.twitter\.com\S+|@\S+|#\S+'
  text = re.sub(regexp, '', text)
  # sub &amp by '&'
  text = re.sub('&amp;', ' and ', text)
  
  # remove urls
  # courtesy of 'https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url'
  url_regex = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
  text = re.sub(url_regex, ' ', text)
  
  # remove twitter handlers
  twitter_handle_regex = '@([A-Za-z0-9_]+)'
  text = re.sub(twitter_handle_regex, ' ', text)
  
  # remove UTF-8 BOM chars
  text = re.sub('�', '', text)
  
  # remove numbers and hashtags
  text = re.sub('([0-9#])', '', text)
  
  #remove special charchters
  text = re.sub('[!@#$]', '', text)
  # remove punctuation
  text = text.translate(str.maketrans('', '', string.punctuation))
  print(text)
  # remove extra whitespaces
  text = re.sub(' +', ' ', text)
	#concatenate
#   text=''.join(text)
 
  return text.lower()	
@api_view(["GET"])
def get_ten(request):
	model=joblib.load("/mnt/c/Users/Mocktar/projects/grad/grad_project_server/venv/graduation/DjangoApi/MyAPI/tweet_model (1).pkl")
	with open('/mnt/c/Users/Mocktar/projects/grad/grad_project_server/venv/graduation/DjangoApi/MyAPI/tokenizer.pickle', 'rb') as handle:
	    tokenizer = pickle.load(handle)
	text=request.data.values()		
	try:
		mydata=list(request.data.values())
		mydata=mydata[0]
		MAX_WORDS = 20
		list_tweets=[]
		
		for tweet in get_tweets(mydata, pages=1):
			if len(list_tweets) <=10:
				list_tweets.append(tweet['text'])
				print(len(list_tweets))
				print(list_tweets) 
		clean_text=[clean_text(tweet) for tweet in list_tweets]
		print(clean_text)		
			#i am dump hahahahhahaah voila le probleme 
			# les erreurs que javais cetait a cause de ca 
			# oblige de creer un hashtag nous meme 
			#unique 
			# ok oui 

		print(list_tweets)		
		# separator = ''
		# X=separator.join(X)
		# entry=X
		# X=[entry]
		# test_samples_tokens = tokenizer.texts_to_sequences(X)
		# predicted_tokenized = pad_sequences(test_samples_tokens, maxlen=MAX_WORDS, padding='post')
		# print(model.predict(predicted_tokenized))
		# y_pred=model.predict_classes(predicted_tokenized)
		# newdf=pd.DataFrame(y_pred, columns=['Status'])
		# newdf=newdf.replace({True:'Positive', False:'Negative'})
		return JsonResponse({ "value":"Success"}, safe=False)
	except ValueError as e:
		return Response(e.args[0], status.HTTP_400_BAD_REQUEST)
@api_view(["GET"])		
def approvereject(request):
	start = time.time()
	model=joblib.load("/mnt/c/Users/Mocktar/projects/grad/grad_project_server/venv/graduation/DjangoApi/MyAPI/tweet_model (1).pkl")
	
	with open('/mnt/c/Users/Mocktar/projects/grad/grad_project_server/venv/graduation/DjangoApi/MyAPI/tokenizer.pickle', 'rb') as handle:
	    tokenizer = pickle.load(handle)

	
	text=request.data.values()		
	try:
		mydata=list(request.data.values())
		mydata=mydata[0]
		MAX_WORDS = 20
		temp_tweet= " fdfdffdf "
		for tweet in get_tweets(mydata, pages=1):
			X=tweet['text']
			temp_tweet=X
		print(X)
		#X=list(mydata.values())
		X=clean_text(X)
		separator = ''
		X=separator.join(X)
		entry=X
		X=[entry]
		test_samples_tokens = tokenizer.texts_to_sequences(X)
		predicted_tokenized = pad_sequences(test_samples_tokens, maxlen=MAX_WORDS, padding='post')
		print(model.predict(predicted_tokenized))
		y_acc=model.predict(predicted_tokenized)
		y_pred=model.predict_classes(predicted_tokenized)
		newdf=pd.DataFrame(y_pred, columns=['Status'])
		newdf=newdf.replace({True:'Positive', False:'Negative'})
		newdf['certainty']=y_acc
		return JsonResponse({ temp_tweet: newdf.iloc[0]['Status'],
		"Certainty": str(newdf.iloc[0]['certainty'])
		}, safe=False)
		
	except ValueError as e:
		return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

print("hello")
end = time.time()
print(end - start)		
