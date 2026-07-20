import requests
base='http://127.0.0.1:5000/api'
print('Starting interview...')
r = requests.post(f'{base}/start-interview', json={'interview_id':'test123','job_role':'Software Engineer'})
print('start response:', r.status_code, r.text)
# Create dummy audio file
with open('tmp_test_audio.webm','wb') as f:
    f.write(b'RIFF....WEBM')
files = {'audio': ('response.webm', open('tmp_test_audio.webm','rb'), 'audio/webm')}
data = {'interview_id':'test123'}
print('Submitting response...')
r2 = requests.post(f'{base}/submit-response', files=files, data=data)
print('submit response:', r2.status_code, r2.text)
