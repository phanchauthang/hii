import pandas as pd
import pickle
import argparse
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import re
import random
import nlpaug.augmenter.word as naw

## torch packages
import torch
from transformers import BertTokenizer,AutoTokenizer
from sklearn.model_selection import train_test_split

## custom packages
import tweet

import pandas as pd

## Label mappings

ed_label_dict = {'Surprised': 0, 'Excited': 1, 'Annoyed': 2, 'Proud': 3, 'Angry': 4, 'Sad': 5, 'Grateful': 6, 'Lonely': 7,
'Impressed': 8, 'Afraid': 9, 'Disgusted': 10, 'Confident': 11, 'Terrified': 12, 'Hopeful': 13, 'Anxious': 14, 'Disappointed': 15,
'Joyful': 16, 'Prepared': 17, 'Guilty': 18, 'Furious': 19, 'Nostalgic': 20, 'Jealous': 21, 'Anticipating': 22, 'Embarrassed': 23,
'Content': 24, 'Devastated': 25, 'Sentimental': 26, 'Caring': 27, 'Trusting': 28, 'Ashamed': 29, 'Apprehensive': 30, 'Faithful': 31}

ed_emo_dict =  {v: k for k, v in ed_label_dict.items()}


isear_label_dict = {"joy":0,"fear":1,"anger":2,"sadness":3,"disgust":4,"shame":5,"guilt":6}

isear_emo_dict = {v: k for k, v in isear_label_dict.items()}

emoint_label_dict = {"anger":0,"fear":1,"joy":2,"sadness":3}

emoint_emo_dict = {v: k for k, v in emoint_label_dict.items()}

goemotions_label_dict= {"admiration":0,"amusement":1,"anger":2, "annoyance":3,"approval":4,"caring":5,"confusion":6,"curiosity":7,"desire":8,"disappointment":9,"disapproval":10,"disgust":11,"embarrassment":12,"excitement":13,"fear":14,"gratitude":15,"grief":16,"joy":17,"love":18,"nervousness":19,"optimism":20,"pride":21,"realization":22,"relief":23,"remorse":24,"sadness":25,"surprise":26}

goemotions_emo_dict = {v: k for k, v in goemotions_label_dict.items()}


target_names_label_dict = {"ed":ed_label_dict,"emoint":emoint_label_dict,"goemotions":goemotions_label_dict,"isear":isear_label_dict}
target_names_emo_dict = {"ed":ed_emo_dict,"emoint":emoint_emo_dict,"goemotions":goemotions_emo_dict,"isear":isear_emo_dict}

def get_one_hot(emo, class_size):

	targets = np.zeros(class_size)
	emo_list = [int(e) for e in emo.split(",")]
	for e in emo_list:
		targets[e-1] = 1
	return list(targets)

def preprocess_data(dataset,tokenizer_type,w_aug,aug_type):
	if aug_type == "syn":
		aug = naw.SynonymAug(aug_src='wordnet')


	if dataset == "ed":
		print("Extracting data")
		data_home = "/content/LCL_loss/data/empathetic_dialogue/"

		data_dict = {}
		for datatype in ["train","valid","test"]:

			if datatype == "train" and w_aug:
				data = pd.read_csv(data_home+datatype+".csv")
				final_prompt,final_emotion = [],[]

				for i,val in enumerate(data["emotion"]):

					final_prompt.append(data["prompt"][i])
					final_emotion.append(val)


				augmented_prompt = aug.augment(final_prompt)


				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_prompt_original =tokenizer.batch_encode_plus(final_prompt).input_ids
				tokenized_prompt_augmented =tokenizer.batch_encode_plus(augmented_prompt).input_ids

				tokenized_combined_prompt = [list(i) for i in zip(tokenized_prompt_original,tokenized_prompt_augmented)]
				combined_prompt = [list(i) for i in zip(final_prompt,augmented_prompt)]
				combined_emotion = [list(i) for i in zip(final_emotion,final_emotion)]

				processed_data = {}


				# ## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_combined_prompt
				processed_data["emotion"] = combined_emotion
				processed_data["cause"] = combined_prompt

				data_dict[datatype] = processed_data

			else:
				data = pd.read_csv(data_home+datatype+".csv")
				final_prompt,final_emotion = [],[]

				for i,val in enumerate(data["emotion"]):

					final_prompt.append(data["prompt"][i])
					final_emotion.append(val)

				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_prompt_original =tokenizer.batch_encode_plus(final_prompt).input_ids

				processed_data = {}


				# ## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_prompt_original
				processed_data["emotion"] = final_emotion
				processed_data["cause"] = final_prompt

				data_dict[datatype] = processed_data


			if w_aug:
				with open("/content/LCL_loss/preprocessed_data/ed_waug_"+aug_type+"_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
				f.close()
			else:
				with open("/content/LCL_loss/preprocessed_data/ed_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
				f.close()

	elif dataset == "emoint":

		data_dict = {}
		data_home = "/content/LCL_loss/data/EmoInt/"

		for datatype in ["train","valid","test"]:
			datafile = data_home + datatype + ".txt"
			## cause => tweet, changed for uniformity sake
			if datatype == "train" and w_aug:
				cause,emotion = tweet.preprocess(datafile,dataset)

				augmented_cause = aug.augment(cause)
				# print(cause)
				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids
				tokenized_cause_augmented =tokenizer.batch_encode_plus(augmented_cause).input_ids


				tokenized_combined_prompt = [list(i) for i in zip(tokenized_cause,tokenized_cause_augmented)]
				combined_prompt = [list(i) for i in zip(cause,augmented_cause)]
				combined_emotion = [list(i) for i in zip(emotion,emotion)]

				processed_data = {}

				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_combined_prompt
				processed_data["emotion"] = combined_emotion
				processed_data["cause"] = combined_prompt

				processed_data = pd.DataFrame.from_dict(processed_data)
				data_dict[datatype] = processed_data
			else:

				cause,emotion = tweet.preprocess(datafile,dataset)

				augmented_cause = aug.augment(cause)
				# print(cause)
				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids

				processed_data = {}

				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_cause
				processed_data["emotion"] = emotion
				processed_data["cause"] = cause
				processed_data = pd.DataFrame.from_dict(processed_data)
				data_dict[datatype] = processed_data


			if w_aug:
				with open("/content/LCL_loss/preprocessed_data/emoint_waug_"+aug_type+"_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
				f.close()
			else:
				with open("/content/LCL_loss/preprocessed_data/emoint_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
				f.close()

	elif dataset == "goemotions":

		data_dict = {}
		data_home = "/content/LCL_loss/data/goemotions/"
		nlabel = 28

		for datatype in ["train","valid","test"]:


			datafile = data_home + datatype + ".tsv"
			## cause => tweet, changed for uniformity sake
			data = pd.read_csv(datafile, sep='\t',names=["cause","emotion","user"])

			emotion,cause = [],[]

			for i,emo in enumerate(data["emotion"]):
				if sum(get_one_hot(emo,nlabel))==1:
					if int(emo) != 27:
						emotion.append(int(emo))
						cause.append(data["cause"][i])

			if datatype == "train" and w_aug:
				augmented_cause = aug.augment(cause)
				# print(cause)
				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids
				tokenized_cause_augmented =tokenizer.batch_encode_plus(augmented_cause).input_ids


				tokenized_combined_prompt = [list(i) for i in zip(tokenized_cause,tokenized_cause_augmented)]
				combined_prompt = [list(i) for i in zip(cause,augmented_cause)]
				combined_emotion = [list(i) for i in zip(emotion,emotion)]

				processed_data = {}

				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_combined_prompt
				processed_data["emotion"] = combined_emotion
				processed_data["cause"] = combined_prompt

				processed_data = pd.DataFrame.from_dict(processed_data)
				data_dict[datatype] = processed_data

			else:
				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids

				processed_data = {}
				maximum_utterance = max([len(i) for i in tokenized_cause])
				average_utterance = np.mean([len(i) for i in tokenized_cause])
				std_utterance = np.std([len(i) for i in tokenized_cause])

				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_cause
				processed_data["emotion"] = emotion
				processed_data["cause"] = cause


				processed_data = pd.DataFrame.from_dict(processed_data)
				data_dict[datatype] = processed_data


			if w_aug:
				with open("/content/LCL_loss/preprocessed_data/goemotions_waug_"+aug_type+"_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
				f.close()
			else:
				with open("/content/LCL_loss/preprocessed_data/goemotions_preprocessed_bert.pkl", 'wb') as f:
					pickle.dump(data_dict, f)
					f.close()

	elif dataset == "isear":
		data = pd.read_csv("/content/LCL_loss/data/ISEAR/ISEAR.csv")
		final_prompt,final_emotion = [],[]

		for i,val in enumerate(data["Field1"]):

			final_prompt.append(data["SIT"][i].replace(f"á\r\n",""))
			final_emotion.append(isear_label_dict[val])


		X_train, X_test_val, y_train, y_test_val = train_test_split(final_prompt,final_emotion, test_size=0.4, random_state=0)

		X_val, X_test, y_val, y_test = train_test_split(X_test_val,y_test_val, test_size=0.5, random_state=0)


		text_dict = {"train":X_train,"valid":X_val,"test":X_test}
		emo_dict  = {"train":y_train,"valid":y_val,"test":y_test}
		data_dict = {}
		for datatype in ["train","valid","test"]:
			cause = text_dict[datatype]
			emotion = emo_dict[datatype]

			if datatype == "train" and w_aug:

				augmented_cause = aug.augment(cause)
				# print(cause)
				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids
				tokenized_cause_augmented =tokenizer.batch_encode_plus(augmented_cause).input_ids


				tokenized_combined_prompt = [list(i) for i in zip(tokenized_cause,tokenized_cause_augmented)]
				combined_prompt = [list(i) for i in zip(cause,augmented_cause)]
				combined_emotion = [list(i) for i in zip(emotion,emotion)]

				processed_data = {}

				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_combined_prompt
				processed_data["emotion"] = combined_emotion
				processed_data["cause"] = combined_prompt

				processed_data = pd.DataFrame.from_dict(processed_data)
				data_dict[datatype] = processed_data

			else:

				print("Tokenizing data")
				tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
				tokenized_cause =tokenizer.batch_encode_plus(cause).input_ids

				processed_data = {}
				maximum_utterance = max([len(i) for i in tokenized_cause])
				average_utterance = np.mean([len(i) for i in tokenized_cause])
				print(len(emotion),len(tokenized_cause))
				print("Max utterance length:",maximum_utterance,"Avg utterance length:",average_utterance)


				## changed prompt --> cause for uniformity
				processed_data["tokenized_cause"] = tokenized_cause
				processed_data["emotion"] = emotion
				processed_data["cause"] = cause
				data_dict[datatype] = processed_data


		if w_aug:
			with open("/content/LCL_loss/preprocessed_data/isear_waug_"+aug_type+"_preprocessed_bert.pkl", 'wb') as f:
				pickle.dump(data_dict, f)
			f.close()
		else:
			with open("/content/LCL_loss/preprocessed_data/isear_preprocessed_bert.pkl", 'wb') as f:
				pickle.dump(data_dict, f)
			f.close()

## use only for subsets
def create_subset(dataset,tokenizer_type,label_list,fname_type,w_aug):


	print("Extracting data")
	data_home = "/content/LCL_loss/data/empathetic_dialogue/"
	aug = naw.SynonymAug(aug_src='wordnet')
	data_dict = {}
	for datatype in ["train","valid","test"]:

		if datatype == "train" and w_aug:
			data = pd.read_csv(data_home+datatype+".csv")
			final_prompt,final_emotion = [],[]

			for i,val in enumerate(data["emotion"]):
				if val in label_list:
					final_prompt.append(data["prompt"][i])
					final_emotion.append(label_list.index(val))

			augmented_prompt = aug.augment(final_prompt)


			print("Tokenizing data")
			tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
			tokenized_prompt_original =tokenizer.batch_encode_plus(final_prompt).input_ids
			tokenized_prompt_augmented =tokenizer.batch_encode_plus(augmented_prompt).input_ids

			tokenized_combined_prompt = [list(i) for i in zip(tokenized_prompt_original,tokenized_prompt_augmented)]
			combined_prompt = [list(i) for i in zip(final_prompt,augmented_prompt)]
			combined_emotion = [list(i) for i in zip(final_emotion,final_emotion)]

			processed_data = {}


			# ## changed prompt --> cause for uniformity
			processed_data["tokenized_cause"] = tokenized_combined_prompt
			processed_data["emotion"] = combined_emotion
			processed_data["cause"] = combined_prompt

			data_dict[datatype] = processed_data

		else:
			data = pd.read_csv(data_home+datatype+".csv")
			final_prompt,final_emotion = [],[]

			for i,val in enumerate(data["emotion"]):
				if val in label_list:
					final_prompt.append(data["prompt"][i])
					final_emotion.append(label_list.index(val))

			print("Tokenizing data")
			tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
			tokenized_prompt_original =tokenizer.batch_encode_plus(final_prompt).input_ids

			processed_data = {}


			# ## changed prompt --> cause for uniformity
			processed_data["tokenized_cause"] = tokenized_prompt_original
			processed_data["emotion"] = final_emotion
			processed_data["cause"] = final_prompt

			data_dict[datatype] = processed_data


	if w_aug:
		fname = "/content/LCL_loss/preprocessed_data/ed_waug_preprocessed_bert_"+fname_type+".pkl"
	else:
		fname = "/content/LCL_loss/preprocessed_data/ed_preprocessed_bert_"+fname_type+".pkl"

	with open(fname, 'wb') as f:
		pickle.dump(data_dict, f)
	f.close()




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Enter tokenizer type')

	parser.add_argument('-d', default="ede",type=str,
				   help='Enter dataset')
	parser.add_argument('-t', default="bert-base-uncased",type=str,
				   help='Enter tokenizer type')
	parser.add_argument('--aug_type', default="syn",type=str,
				   help='Enter augmentation type')
	parser.add_argument('--aug', action='store_true')
	parser.add_argument('--subset', action='store_true')
	args = parser.parse_args()


	if not args.subset:
		preprocess_data(args.d,args.t,w_aug=args.aug,aug_type=args.aug_type)
	else:
	## for subset input label_list,fname
		label_list = []
		fname = ""
		if len(label_list) == 0 or fname == "":
  			raise Exception("Enter the list of labels to be included in subset and name of the file")
		create_subset(args.d,args.t,label_list,fname,args.aug)


