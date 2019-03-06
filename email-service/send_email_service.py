#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import time

def record():
	list_sent = []
	try:
		filerecord = open(r'./record.txt', 'r+')
	except:
		return []
	for f in filerecord.readlines():
			f=f[:-1]
			list_sent.append(f)

	filerecord.close()
	for a in list_sent:
		if a == '\n':
			list_sent.remove(a)
	return list_sent
	
def add(list_sent):
	filerecord=open(r'./record.txt', 'w')
	for a in list_sent:
		filerecord.write(a)
		filerecord.write('\n')
	filerecord.close()
	
def file_name(file_dir):
	list_original = []
	for root, dirs, files in os.walk(file_dir):
		for f in files:
			list_original.append(f)

	list_original.remove('.DS_Store')
	list_original.remove('capture3.pde')
	return list_original


def main():
	email_address = "hilxc1993@gmail.com"
	folder_to_listen = './capture3'
	print("Service started!")
	while True:
	#	path = r'/Users/mac/Documents/Final Master Project/Python functions/图片库'
		
		# read sent photos
		list_sent = record()
			# list all photos
		list_original = file_name(folder_to_listen)
		
		list_difference = set(list_original).difference(set(list_sent))
		
		if len(list_difference) != 0:
			for f_name in list_difference:
				b = ''.join(f_name)
				list_sent.append(f_name)
				photo_path = folder_to_listen + '/' + b
				print(photo_path)
				from os.path import basename
				from email.mime.text import MIMEText
				from subprocess import Popen, PIPE
				from email.MIMEBase import MIMEBase
				from email.mime.application import MIMEApplication
				from email.mime.multipart import MIMEMultipart
				msg = MIMEMultipart()
				msg["To"] = email_address
				msg["Subject"] = "New image for twitter"

				with open(photo_path, "rb") as fil:
					part = MIMEApplication(
						fil.read(),
						Name=basename(photo_path)
					)
				part['Content-Disposition'] = 'attachment; filename="%s"' % basename(photo_path)
				msg.attach(part)
				p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
				p.communicate(msg.as_string())
				
		add(list_sent)
		
		time.sleep(30)
	


if __name__ == '__main__':
	main()
