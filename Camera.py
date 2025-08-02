import numpy as np
from MathLib import *

class Camera:
    def __init__(self, width=800, height=600):
        self.position = np.array([0, 0, 5], dtype=np.float32)
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        
        self.fov = 60
        self.aspect = width / height
        self.near = 0.1
        self.far = 1000.0

        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = width
        self.viewport_height = height
        
    def set_position(self, x, y, z):
        self.position = np.array([x, y, z], dtype=np.float32)
    
    def set_target(self, x, y, z):
        self.target = np.array([x, y, z], dtype=np.float32)
        
    def set_up(self, x, y, z):
        self.up = np.array([x, y, z], dtype=np.float32)
        
    def set_projection(self, fov=None, aspect=None, near=None, far=None):
        if fov is not None: self.fov = fov
        if aspect is not None: self.aspect = aspect
        if near is not None: self.near = near
        if far is not None: self.far = far
        
    def set_viewport(self, x=None, y=None, width=None, height=None):
        if x is not None: self.viewport_x = x
        if y is not None: self.viewport_y = y
        if width is not None: self.viewport_width = width
        if height is not None: self.viewport_height = height
        
    def get_view_matrix(self):
        return LookAtMatrix(self.position, self.target, self.up)
    
    def get_projection_matrix(self):
        return ProjectionMatrix(self.fov, self.aspect, self.near, self.far)
    
    def get_viewport_matrix(self):
        return ViewportMatrix(self.viewport_x, self.viewport_y, 
                            self.viewport_width, self.viewport_height)
    
    def orbit_around_target(self, horizontal_angle, vertical_angle, distance=None):
        if distance is None:
            distance = np.linalg.norm(self.position - self.target)
            
        h_rad = np.radians(horizontal_angle)
        v_rad = np.radians(vertical_angle)
        
        x = self.target[0] + distance * np.cos(v_rad) * np.sin(h_rad)
        y = self.target[1] + distance * np.sin(v_rad)
        z = self.target[2] + distance * np.cos(v_rad) * np.cos(h_rad)
        
        self.position = np.array([x, y, z], dtype=np.float32)
    
    def move_forward(self, distance):
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)
        
        self.position += forward * distance
        self.target += forward * distance
    
    def move_right(self, distance):
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)
        
        self.position += right * distance
        self.target += right * distance
    
    def move_up(self, distance):
        up = self.up / np.linalg.norm(self.up)
        
        self.position += up * distance
        self.target += up * distance
    
    def look_at(self, target):
        self.target = np.array(target, dtype=np.float32)