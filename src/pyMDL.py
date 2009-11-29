import struct
import Image
import sys



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
	


class PyMDL:
	#FORMAT = "<lllllls"
	
	def __init__(self):
		self.data = None

	def convertToPNG(self, filename):
		reader = FileReader(filename)
			
		#(magic, version, libcount, symcount, extcount, zero, model) = struct.unpack(PyMDL.FORMAT, file.read(struct.calcsize(PyMDL.FORMAT)))

		magic = reader.read_int('l')
		assert magic == -558178560
		version = reader.read_int('l')
		assert version == 65536
		libcount = reader.read_int('l')
		symcount = reader.read_int('l')
		assert symcount == 1           # FIXME: more is valid, but currently just not supported
		extcount = reader.read_int('l')
		zero = reader.read_int('l')
		assert zero == 0
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
	
		data = reader.read_bytes(binary_surface_info['x'] * binary_surface_info['y'] * binary_surface_info['bitCount']/8)

		object_end = reader.read_int('l')
		assert object_end == 0
		
		print 'libcount: %i' % libcount
		print 'symcount: %i' % symcount
		print 'extcount: %i' % extcount
		print 'libs: %s' % ', '.join(libs)
		print 'symbols: %s' % ', '.join(symbols)
		print 'externals: %s' % ', '.join(externals)
		
		print 'bitCount: %i' % binary_surface_info['bitCount']
		print 'blueMask: %i' % binary_surface_info['blueMask']
		print 'len(data): %i' % len(data)
		
		





if(__name__ == "__main__"):
	if len(sys.argv) < 2:
		print "Syntax: pyMDL.py <file to convert>"
	else:
		pyMDL = PyMDL()
		pyMDL.convertToPNG(sys.argv[1])
