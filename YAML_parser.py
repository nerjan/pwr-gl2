import yaml
import copy
from random import sample


class IOError(Exception, yaml.SafeLoader):
    """Basic exception for errors raised"""

    def __init__(self, err, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occured with reading questions %s" % err
        super(IOError, self).__init__(msg)
        self.err = err


class Qread(IOError):

    def __init__(self, filename='questions.yaml'):
        self.__dicts = []
        self.filename = filename
        with open(self.filename, 'r') as fileio:
            try:
                self.__yamldict = yaml.load_all(fileio)
            except yaml.YAMLError as exc:
                print(exc)
            for s in self.__yamldict:
                self.__dicts.append(copy.deepcopy(s))
            self.__numdoc = len(self.__dicts)

    def qallread(self):
        """Returns question generator for all questions in yaml file"""
        for s in range(self.__numdoc):
            self.current = self.__dicts[s]
            yield self.current

    def qnumread(self, number):
        """Returns question generator based till a number"""
        if number > self.__numdoc:
            raise IOError("The requested number is higher"
                          "than avialable documents in YAML file")
        else:
            newdict = self.__dicts[:number]
            for s in range(len(newdict)):
                self.current = self.__dicts[s]
                yield self.current

    def qkeysread(self, keys=[]):
        """Returns question generator based on key indicies"""
        if len(keys) > self.__numdoc or max(keys) > (self.__numdoc-1):
            raise IOError("The requested number is higher"
                          "than avialable documents in YAML file"
                          "or one of the keys is too high")
        else:
            for s in keys:
                self.current = self.__dicts[s]
                yield self.current

    def qlen(self):
        """Number of questions in YAML file"""
        return self.__numdoc

    def qreloadfile(self):
        """Reload yaml file (for example, after update)"""
        self.__init__(self.filename)


class Qshuffle(Qread):

    def qshuffleall(self):
        """Shuffles questions"""
        randomkeys = sample(range(self.qlen()), self.qlen())
        return self.qkeysread(randomkeys)

    def qshuffleans(self):
        """Shuffles answers inside all questions"""
        for s in self.qallread():
            randomkeys = sample(range(len(s['answers'])), len(s['answers']))
            prev = s['answers']['answer'+str(randomkeys[len(s['answers'])-1]+1)]
            for d in range(len(s['answers'])-1):
                next = s['answers']['answer'+str(randomkeys[d+1]+1)]
                s['answers']['answer'+str(randomkeys[d+1]+1)] = prev
                prev = next

    def qshufflenum(self):
        pass

    def qlist(self):
        """Return a dictionary in form of question:[answer1, answer2 ...
        answern]"""
        return {s['value']: [s['answers']['answer'+str(d+1)]['value']
                             for d in range(len(s['answers']))]
                                for s in self.qallread()}

    def qcurscorelist(self):
        """Return  score for current generator's element"""
        return [self.current['answers']['answer'+str(s+1)]['value']
                    for s in range(len(self.current['answers']))]

    def qcurque(self):
        """Return question for current generator's element"""
        return self.current['value']


if __name__ == '__main__':
    newq = Qread()
    print('###TEST1###')
    print(newq.qallread())
    print('###TEST2###')
    print(newq.qlen())
    print('###TEST3###')
    print(newq.qkeysread([1]))
    print('###TEST4###')
    print(newq.qnumread(2))
    newSQ = Qshuffle()
    print('###TEST5###')
    print(newSQ.qlen())
    print('###TEST6###')
    x = newSQ.qshuffleall()
    for z in x:
        print('###TEST7###')
        print(newSQ.qshuffleans())
        print(z)
    print(newSQ.qlist())
