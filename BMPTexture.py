import struct

class BMPTexture:
    def __init__(self, filename):
        self.width = 0
        self.height = 0
        self.pixels = []
        self.load(filename)
    
    def load(self, filename):
        with open(filename, 'rb') as file:
            if file.read(2) != b'BM':
                raise ValueError("No es un archivo BMP válido")
            
            file.seek(10)
            pixel_data_offset = struct.unpack('<I', file.read(4))[0]
            
            file.seek(18)
            self.width = struct.unpack('<I', file.read(4))[0]
            self.height = struct.unpack('<I', file.read(4))[0]
            file.seek(28)
            bits_per_pixel = struct.unpack('<H', file.read(2))[0]
            
            if bits_per_pixel != 24:
                raise ValueError("Solo se admiten archivos BMP de 24 bits")
            
            file.seek(pixel_data_offset)
            self.pixels = [[(0, 0, 0) for _ in range(self.height)] for _ in range(self.width)]
            
            for y in range(self.height-1, -1, -1):
                for x in range(self.width):
                    b, g, r = struct.unpack('<BBB', file.read(3))
                    self.pixels[x][y] = (r/255, g/255, b/255)  
                
                padding = (4 - (self.width * 3) % 4) % 4
                file.read(padding)
    
    def get_color(self, u, v):
        """Obtiene el color en las coordenadas de textura (u, v) normalizadas (0-1)"""
        if not self.pixels:
            return (1, 1, 1)  
        
        u = u % 1.0
        v = v % 1.0
        
        x = int(u * (self.width - 1))
        y = int((1 - v) * (self.height - 1))  
        
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return self.pixels[x][y]