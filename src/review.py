#import google.generativeai as genai
from google import genai
from google.genai import types
import sys, os, io
import argparse
from dotenv import load_dotenv
from pathlib import Path

model = None
api_key = ''
dict_ext = ['.json']
script_dir = Path(__file__).parent
env_file = script_dir.parent / '.env'
load_dotenv(dotenv_path=env_file)
client = genai.Client(api_key=os.getenv('VUE_APP_GEMINI_API_KEY'))

def main():

  parser = argparse.ArgumentParser(description="ディレクトリ")
  parser.add_argument('dir', type=str, help='対象ディレクトリ')
  args = parser.parse_args()

  if args.dir is not None:
    content = []
    for root, dirs, files in os.walk(args.dir):
      for file in files:
        print(os.path.join(root, file))
        with open(os.path.join(root, file), 'rb') as file_bin:
          file_content = file_bin.read()
          bytes_file = io.BytesIO(file_content)
          content.append(uploadFileGemini(os.path.join(root, file)))

    request = [*content, createPrompt()]
    calcToken(request)
    response = client.models.generate_content(
      model=os.getenv("USE_GEMINI_MODEL"),
      contents=request
    )

    print(response.text)
    with open('./response.txt', 'w', encoding='utf-8') as file:
      file.write(response.text)
    dropUploadFile()
  else:
    print('missing arg')
  
  print('done')

def uploadFileGemini(fileIo):
  _, ext = os.path.splitext(fileIo)
  ext = ext.lower()
  if ext in ['.py']:
    mimeType = 'text/x-python'
  elif ext in ['.js']: 
    mimeType = 'text/javascript'
  else:
    mimeType = 'text/plain'
  return client.files.upload(file=fileIo, config=dict(
    mime_type = mimeType
  ))

def dropUploadFile():
  for file in client.files.list():
    print("delete:", file.name)
    client.files.delete(name=file.name)

def createPrompt():
  return 'あなたは有能なSEです。プログラム上の不具合や品質の低いコードの箇所を指摘してください。'

def calcToken(request):
  response = client.models.count_tokens(model=os.getenv("USE_GEMINI_MODEL"), contents=request)
  return str(response.total_tokens)

if __name__ == "__main__":
  main()