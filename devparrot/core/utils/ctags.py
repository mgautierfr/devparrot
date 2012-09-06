#!/usr/bin/python

import os

class Ctags_file:
    def __init__(self, filename):
        self.filename = filename
        self.file = file(self.filename, "r")
        pass
    
    def get_tag(self, tag):
        self.file.seek(0, os.SEEK_END)
        high = self.file.tell()
        self.file.seek(0, os.SEEK_SET)
        return self.look_for_tag(tag, 0, high)
 
 	def look_for_tag(self, tag, low, high):
        current = int((high+low)/2)
        
        self.file.seek(current)
        self.file.readline()
        new_current = self.file.tell()
        if new_current >= high:
            return None
        line = self.file.readline()
        line_elem = line.split('\t')
        if line_elem[0] == tag:
            return self.get_tag_list(tag, new_current)
        if line_elem[0] < tag:
            return self.look_for_tag(tag, current, high)
        else:
            return self.look_for_tag(tag, low, new_current)
        pass
    
    def get_tag_list(self, tag, current):
        found_tag = tag
        while(found_tag==tag):
            # 256 is the maximal line handle by vi
            self.file.seek(current-256)
            current = self.file.tell()
            self.file.readline()
            line = self.file.readline()
            line_elem = line.split('\t')
            found_tag = line_elem[0]
        while(found_tag!=tag):
            line =self.file.readline()
            line_elem = line.split('\t')
            found_tag = line_elem[0]
        tag_obj = Tag(tag)
        while(found_tag==tag):
            tag_obj.add_location(line[:-1])
            line =self.file.readline()
            line_elem = line.split('\t')
            found_tag = line_elem[0]
        return tag_obj
    
class Tag:
    class Location:
        def __init__(self, elems):
            self.file = elems[0]
            self.founders = []
            self.extras = {}
            extra_line = "\t".join(elems[1:])
            founders = extra_line.split(';')
            i = 0
            end = False
            while not end:
                founder = founders[i]
                if not founder.startswith('"'):
                    self.founders.append(founder)
                    i += 1
                else:
                    end = True
            extra_line = ";".join(founders[i:])
            extras = extra_line.split('\t')[1:]
            for extra in extras:
                extras = extra.split(':')
                if len(extras) == 1:
                    name = "kind"
                    value = extras[0]
                else:
                    name = extras[0]
                    value = extras[1]
                self.extras[name] = value

        def __str__(self):
            return "%(file)s [ %(founders)s ] { %(extras)s }"%{
                    'file': self.file,
                    'founders': ",".join(self.founders),
                    'extras' : ",".join(["%s:%s"%(name,value) for (name,value) in self.extras.items()])
                }
        
        def pprint(self):
            print "%(file)s:%(founders)s"%{'file': self.file,'founders': ",".join(self.founders)}
        
    

    def __init__(self, tag):
        self.name = tag
        self.locations = [] 
    
    def add_location(self, line):
        elems = line.split('\t')
        if self.name != elems[0]:
            return
        self.locations.append(Tag.Location(elems[1:]))

    def __str__(self):
        return "Tag %(name)s : \n%(locations)s"%{
            'name':self.name,
            'locations': "["+"\n".join([str(l) for l in self.locations])+"]"
        }
        
    def pprint(self):
        print self.name
        for loc in self.locations:
            loc.pprint() 

if __name__ == "__main__":
    import sys
    print sys.argv
    if len(sys.argv) == 1:
        print "No arguments"
        sys.exit(0)
    print "Looking for element", sys.argv[1]
    ctagf = Ctags_file("tags")
    tag = ctagf.get_tag(sys.argv[1])
    print tag
    if tag:
        tag.pprint()
    else:
        print "No tag found"
