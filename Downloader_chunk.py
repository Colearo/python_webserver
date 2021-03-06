#!/usr/bin/python3
# encoding=utf-8
'''
    这是一个支持HTTP断点续传的客户端下载器
    使用时命令为python3 download_get.py -u http://somesite.com:port/file
'''

import requests, sys, os, re, time
from optparse import OptionParser


class wget:
	def __init__(self, config = {}):
		self.config = {
			'block': int(config['block'] if 'block' in config else 1024),
		}
		self.total = 0
		self.size = 0
		self.filename = ''

	def touch(self, filename):
		with open(filename, 'w') as fin:
			pass

	def remove_nonchars(self, name):
		(name, _) = re.subn(r'[\\\/\:\*\?\"\<\>\|]','',name)
		return name
		
	def support_continue(self, url):
		headers = {
			'Range': 'bytes=0-4'
		}
		try:
			r_a = requests.head(url, headers = headers)
			crange = r_a.headers['Content-Range']
			self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
			return True
		except:
			pass
		try:
			self.total = int(r_a.headers['Content-Length'])
		except:
			self.total = 0
		return False


	def download(self, url, filename, headers = {}):
		finished = False
		block = self.config['block']
		local_filename = self.remove_nonchars(filename)
		tmp_filename = local_filename + '.ddtmp'
		size = self.size
		
	
		if self.support_continue(url):  # 支持断点续传
			try:
				with open(tmp_filename, 'rb') as fin:
					self.size = int(fin.read())
					size = self.size + 1
			except:
				self.touch(tmp_filename)
			finally:
				headers['Range'] = "bytes=%d-" % (self.size, )
		else:
			self.touch(tmp_filename)
			self.touch(local_filename)
		total = self.total
		r = requests.get(url, stream = True, verify = False, headers = headers)
		if total > 0:
			print ("[+] Size: %dKB" % (total / 1024))
		else:
			print ("[+] Size: None")
		#start_t = time.time()
		with open(local_filename, 'ab+') as f:
			f.seek(self.size)
			f.truncate()
			try:
				for chunk in r.iter_content(chunk_size = block): 
					if chunk:
						f.write(chunk)
						size += len(chunk)
						f.flush()
					sys.stdout.write('\b' * 64 + 'Now: %d, Total: %s' % (size, total))
					sys.stdout.flush()
				finished = True
				os.remove(tmp_filename)
				#spend = int(time.time() - start_t)
				#speed = int((size - self.size) / 1024 / spend)
				#sys.stdout.write('\nDownload Finished!\nTotal Time: %ss, Download Speed: %sk/s\n' % (spend, speed))
				sys.stdout.write('\nDownload Finished!\n')
				sys.stdout.flush()
			except:
				# import traceback
				# print traceback.print_exc()
				print ("\nDownload pause.\n")
			finally:
				if not finished:
					with open(tmp_filename, 'wb') as ftmp:
						ftmp.write(str(size).encode("utf-8"))
						
if __name__ == '__main__':
    
	parser = OptionParser()
	parser.add_option("-u", "--url", dest="url",  
	                  help="target url")
	parser.add_option("-o", "--output", dest="filename",  
	                  help="download file to save")
	parser.add_option("-a", "--user-agent", dest="useragent", 
					  help="request user agent", default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 \
			(KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36')
	parser.add_option("-r", "--referer", dest="referer", 
					  help="request referer")
	parser.add_option("-c", "--cookie", dest="cookie", 
					  help="request cookie", default = 'foo=1;')
	(options, args) = parser.parse_args()
    
	if not options.url:
		print ('Missing url')
		sys.exit()
	if not options.filename:
		options.filename = options.url.split('/')[-1]
	headers = {
		'User-Agent': options.useragent,
		'Referer': options.referer if options.referer else options.url,
		'Cookie': options.cookie
	}
	start_t = time.time()
	wget().download(options.url, options.filename)
	print("Cost: %d s" % (time.time()-start_t))
