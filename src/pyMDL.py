import struct
import Image, ImageFile
import sys, os

class NotMDLException(SyntaxError):
  pass

class NotImplementedException(SyntaxError):
  pass

class FileReader:
	def __init__(self, filename):
		with open(filename, 'rb') as file:
			self.data = file.read()
		self.pos = 0
	
	def read_strings(self, count):
		result = []
		for i in xrange(count):
			char = self.data[self.pos]
			result.append("")
			while char != '\0':
				result[i] += char
				self.pos += 1
				char = self.data[self.pos]
			self.pos += 4-(self.pos%4)
		return result
		
	def read_int(self, type):
		result = struct.unpack_from('<' + type, self.data[self.pos:])
		self.pos += struct.calcsize(type)
		return int(result[0])
			
	def read_bytes(self, count):
		result = self.data[self.pos:self.pos+count]
		self.pos += count
		return result
	

#http://www.pythonware.com/library/pil/handbook/decoder.htm
class MDLImageFile(ImageFile.ImageFile):

  format = "MDL"
  format_description = "Allegiance™ MDL version 1 image file"
  
	#FORMAT = "<lllllls"
	
	def _open(self):
		reader = FileReader(self.fp) #TODO: confirm self.fp is a file-like object.
			
		#(magic, version, libcount, symcount, extcount, zero, model) = struct.unpack(PyMDL.FORMAT, file.read(struct.calcsize(PyMDL.FORMAT)))

		magic = reader.read_int('l')
		if not magic == -558178560:
		  raise NotMDLException, "%s is not a valid compiled MDL file." % filename
		version = reader.read_int('l')
		if not version>>16 == 1:
		  raise NotImplementedException, "%s is a version %d MDL file; this application only supports version 1." % (filename, version>>16)
		  #bonus points: set version bytes to 70000 and send the output to 
		libcount = rfilename, eader.read_int('l')
		symcount = reader.read_int('l')
		if not symcount == 1:           # FIXME: more is valid, but currently just not supported
		  raise NotImplementedException, "%s file contains %d symbols. This tool only supports one symbol per file." % (filename, symcount)
		extcount = reader.read_int('l')
		zero = reader.read_int('l')
		if not zero == 0:
		  raise NotImplementedException, "%s is not a valid version 1 MDL file from FreeAllegiance." % filename
		libs = reader.read_strings(libcount)
		indexNameSpaceTable = reader.read_int('l')
		symbols = reader.read_strings(symcount)
		externals = reader.read_strings(extcount)
		
		index_of_first_def = reader.read_int('l')
		ref_type = reader.read_int('l')
		assert ref_type == 9		 # TODO: should be 9, actually
		ref_index = reader.read_int('l')
		assert ref_index == 0
		marker_object_binary = reader.read_int('l')
		assert marker_object_binary == 7
		
		binary_surface_info = {}
		binary_surface_info['x'] = reader.read_int('l')
		binary_surface_info['y'] = reader.read_int('l')
		binary_surface_info['pitch'] = reader.read_int('l')
		binary_surface_info['bitCount'] = reader.read_int('l')
		assert binary_surface_info['bitCount'] == 16
		binary_surface_info['redMask'] = reader.read_int('l')
		binary_surface_info['greenMask'] = reader.read_int('l')
		binary_surface_info['blueMask'] = reader.read_int('l')
		binary_surface_info['alphaMask'] = reader.read_int('l')
		binary_surface_info['bColorKey'] = reader.read_int('?xxx')
		
		self.size = binary_surface_info['x'], binary_surface_info['y']
		self.mode = "F;16" #TODO: check if the image is actually a "16-bit little endian unsigned integer"
		self.tile = [("raw", #use the raw decoder on the image
		              (0,0)+self.size, #of self.size size
		              reader.pos, #starting from this offset
		              (self.mode, #in this mode
		               0, #with 0 padding between lines
		               1, #starting from the top (-1 to start from the bottom)
		               ))]
	
#		data = reader.read_bytes(binary_surface_info['x'] * binary_surface_info['y'] * binary_surface_info['bitCount']/8)
#		object_end = reader.read_int('l')
#		assert object_end == 0
		
		print filename, 'libcount: %i' % libcount
		print filename, 'symcount: %i' % symcount
		print filename, 'extcount: %i' % extcount
		print filename, 'libs: %s' % ', '.join(libs)
		print filename, 'symbols: %s' % ', '.join(symbols)
		print filename, 'externals: %s' % ', '.join(externals)
		print filename, 'size: %ix%i' % (binary_surface_info['x'], binary_surface_info['y'])
		print filename, 'bitCount: %i' % binary_surface_info['bitCount']
		print filename, 'redMask: %i' % binary_surface_info['redMask']
		print filename, 'greenMask: %i' % binary_surface_info['greenMask']
		print filename, 'blueMask: %i' % binary_surface_info['blueMask']
		print filename, 'len(data): %i' % len(data)

#now register.
Image.register_open("MDL", MDLImageFile)
Image.register_extension("MDL", ".mdl")

#http://code.activestate.com/recipes/180801/
if(__name__ == "__main__"):
	if len(sys.argv) < 2:
		print "Syntax: pyMDL.py <file(s) to convert>"
	else:
		for mdlFile in sys.argv[1:]:
		  try:
		    pngFile = os.path.splitext(mdlFile)[0] + ".png"
    		Image.open(mdlFile).save(pngFile)
  		except Exception e:
        print mdlFile, e
