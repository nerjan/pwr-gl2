import yaml
import copy
from random import sample
class IOError(Exception,yaml.SafeLoader):
    """Basic exception for errors raised"""
    def __init__(self, err, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occured with reading questions %s" % err
        super(IOError, self).__init__(msg)
        self.err = err
class Qread(IOError):
	def __init__(self,filename='questions.yaml'):
		self.__dicts=[]
		self.filename=filename
		self.__fileio=open(self.filename, 'r')
		try:
			self.__yamldict=yaml.load_all(self.__fileio)
		except yaml.YAMLError as exc:
			print(exc)
		for s in self.__yamldict:
			self.__dicts.append(copy.deepcopy(s))
		self.__numdoc=len(self.__dicts)
		self.__fileio.close()
#Returns question generator for all questions in yaml file
	def qallread(self):
		#return self.__dicts
		for s in range(self.__numdoc):
			self.current=self.__dicts[s]
			yield self.current	
#Returns question generataor based till a number	
	def qnumread(self,number):
		if number > self.__numdoc:
			raise IOError("The requested number is higher than avainable documents in YAML file")
		else:
			#return self.__dicts[:number]
			newdict=self.__dicts[:number]
			for s in range(len(newdict)):
				self.current=self.__dicts[s]
				yield self.current
#Returns question generator based on key indicies
	def qkeysread(self,keys=[]):
		if len(keys) > self.__numdoc or max(keys) > (self.__numdoc-1):
			raise IOError("The requested number is higher than avainable documents in YAML file or one of the keys is too high")
		else:
			#return [self.__dicts[s] for s in keys]
			for s in keys:
				self.current=self.__dicts[s]
				yield self.current
#Number of questions in YAML file
	def qlen(self):
		return self.__numdoc
#Reload yaml file (for example, after update)
	def qreloadfile(self):
		self.__init__()
class Qshuffle(Qread):
#Shuffles questions
	def qshuffleall(self):
		randomkeys=sample(range(self.qlen()),self.qlen())
		return self.qkeysread(randomkeys)
#Shuffles answers inside all questions
	def qshuffleans(self):
		for s in self.qallread():
		#s=self.current
		#print(s['answers'])
			randomkeys=sample(range(len(s['answers'])),len(s['answers']))
			prev=s['answers']['answer'+str(randomkeys[len(s['answers'])-1]+1)]
			for d in range(len(s['answers'])-1):
				next=s['answers']['answer'+str(randomkeys[d+1]+1)]
				s['answers']['answer'+str(randomkeys[d+1]+1)]=prev
				prev=next
		#return questions
	def qshufflenum(self):
		pass
	#def qcuranslist(self):
		#return [self.current['answers']['answer'+str(s+1)]['value'] for s in range(len(self.current['answers']))]
#Return a dictionary in form of question:[answer1, answer2 ... answern]#
	def qlist(self):
		return {s['value']:[s['answers']['answer'+str(d+1)]['value']  for d in range(len(s['answers']))] for s in self.qallread()}
#Return  score for current generator's element#
	def qcurscorelist(self):
		return [self.current['answers']['answer'+str(s+1)]['value'] for s in range(len(self.current['answers']))]
#Return question for current generator's element#
	def qcurque(self):
		return self.current['value']

if __name__ == '__main__':
	newq=Qread()
	print('###TEST1###')
	print(newq.qallread())
	print('###TEST2###')
	print(newq.qlen())
	print('###TEST3###')
	print(newq.qkeysread([1]))
	print('###TEST4###')
	print(newq.qnumread(2))
	newSQ=Qshuffle()
	print('###TEST5###')
	print(newSQ.qlen())
	print('###TEST6###')
	x=newSQ.qshuffleall()
	for z in x:
		print('###TEST7###')
		print(newSQ.qshuffleans())
		print(z)
	print(newSQ.qlist())
