#Universidad del Valle de Guatemala
#Fernando José Garavito Ovando 18071
#Graficas por Computadoras
#Lab 4: Shaders II

from pygame import image
import glm
from numpy import array, float32
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import obj

class ModelObj(object):
    def __init__(self, objName, textureName):
        self.model = obj.Obj(objName)
        self.createVertexBuffer()
        self.position = glm.vec3(0,0,0)
        self.rotation = glm.vec3(0,0,0)
        self.scale = glm.vec3(1,1,1)
        self.textureSurface = image.load(textureName)
        self.textureData = image.tostring(self.textureSurface, "RGB", True)
        self.texture = glGenTextures(1)


    def getModelMatrix(self):
        identity = glm.mat4(1)
        translateMatrix = glm.translate(identity, self.position)
        pitch = glm.rotate(identity, glm.radians( self.rotation.x ), glm.vec3(1,0,0) )
        yaw   = glm.rotate(identity, glm.radians( self.rotation.y ), glm.vec3(0,1,0) )
        roll  = glm.rotate(identity, glm.radians( self.rotation.z ), glm.vec3(0,0,1) )
        rotationMatrix = pitch * yaw * roll
        scaleMatrix = glm.scale(identity, self.scale)
        return translateMatrix * rotationMatrix * scaleMatrix

    def createVertexBuffer(self):
        buffer = []
        for face in self.model.faces:
            for i in range(3):
                pos = self.model.vertices[face[i][0] - 1]
                buffer.append(pos[0])
                buffer.append(pos[1])
                buffer.append(pos[2])
                norm = self.model.normals[face[i][2] - 1]
                buffer.append(norm[0])
                buffer.append(norm[1])
                buffer.append(norm[2])
                
                uvs = self.model.texcoords[face[i][1] - 1]
                buffer.append(uvs[0])
                buffer.append(uvs[1])

        self.vertBuffer = array(buffer, dtype = float32)
        self.VBO = glGenBuffers(1) 
        self.VAO = glGenVertexArrays(1) 

    def renderInScene(self):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER,           
                     self.vertBuffer.nbytes,    
                     self.vertBuffer,           
                     GL_STATIC_DRAW )           

        glVertexAttribPointer(0,                
                              3,                
                              GL_FLOAT,         
                              GL_FALSE,         
                              4 * 8,            
                              ctypes.c_void_p(0)) 

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1,
                              3,
                              GL_FLOAT,
                              GL_FALSE,
                              4 * 8,
                              ctypes.c_void_p(4 * 3))

        glEnableVertexAttribArray(1)
        
        glVertexAttribPointer(2,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              4 * 8,
                              ctypes.c_void_p(4 * 6))

        glEnableVertexAttribArray(2)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D,                     
                     0,                                 
                     GL_RGB,                            
                     self.textureSurface.get_width(),   
                     self.textureSurface.get_height(),  
                     0,                                 
                     GL_RGB,                            
                     GL_UNSIGNED_BYTE,                  
                     self.textureData)                  

        glGenerateMipmap(GL_TEXTURE_2D)

        glDrawArrays(GL_TRIANGLES, 0, len(self.model.faces) * 3 ) # Para dibujar vertices en orden

class Proppp(object):
    def __init__(self, verts, indices):
        self.createVertexBuffer(verts, indices)
        self.position = glm.vec3(0,0,0)
        self.rotation = glm.vec3(0,0,0)
        self.scale = glm.vec3(1,1,1)
    
    def getModelMatrix(self):
        identity = glm.mat4(1)
        translateMatrix = glm.translate(identity, self.position)
        pitch = glm.rotate(identity, glm.radians( self.rotation.x ), glm.vec3(1,0,0) )
        yaw   = glm.rotate(identity, glm.radians( self.rotation.y ), glm.vec3(0,1,0) )
        roll  = glm.rotate(identity, glm.radians( self.rotation.z ), glm.vec3(0,0,1) )
        rotationMatrix = pitch * yaw * roll
        scaleMatrix = glm.scale(identity, self.scale)
        return translateMatrix * rotationMatrix * scaleMatrix

    def createVertexBuffer(self, verts, indices):
        self.vertBuffer = verts
        self.indexBuffer = indices
        self.VBO = glGenBuffers(1) 
        self.VAO = glGenVertexArrays(1) 
        self.EAO = glGenBuffers(1) 

    def renderInScene(self):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EAO)

        glBufferData(GL_ARRAY_BUFFER,           
                     self.vertBuffer.nbytes,    
                     self.vertBuffer,           
                     GL_STATIC_DRAW )           

        glBufferData(GL_ELEMENT_ARRAY_BUFFER,   
                     self.indexBuffer.nbytes,    
                     self.indexBuffer,           
                     GL_STATIC_DRAW )           
        
        glVertexAttribPointer(0,                
                              3,                
                              GL_FLOAT,         
                              GL_FALSE,         
                              4 * 6,            
                              ctypes.c_void_p(0)) 

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1,                
                              3,                
                              GL_FLOAT,         
                              GL_FALSE,         
                              4 * 6,            
                              ctypes.c_void_p(4 * 3)) 

        glEnableVertexAttribArray(1)
        
        glDrawElements(GL_TRIANGLES, len(self.indexBuffer), GL_UNSIGNED_INT, None) #Para dibujar con indices
    
class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)
        self.scene = []
        self.pointLight = glm.vec3(-10, 0, -5)
        self.tiempo = 0
        self.valor = 0
        self.camPosition = glm.vec3(0,0,0)
        self.camRotation = glm.vec3(0,0,0) 
        self.projectionMatrix = glm.perspective(glm.radians(60),            # FOV en radianes
                                                self.width / self.height,   # Aspect Ratio
                                                0.1,                        # Near Plane distance
                                                1000)                       # Far plane distance

    def getViewMatrix(self):
        identity = glm.mat4(1)
        translateMatrix = glm.translate(identity, self.camPosition)
        pitch = glm.rotate(identity, glm.radians( self.camRotation.x ), glm.vec3(1,0,0) )
        yaw   = glm.rotate(identity, glm.radians( self.camRotation.y ), glm.vec3(0,1,0) )
        roll  = glm.rotate(identity, glm.radians( self.camRotation.z ), glm.vec3(0,0,1) )

        rotationMatrix = pitch * yaw * roll
        camMatrix = translateMatrix * rotationMatrix

        return glm.inverse(camMatrix)

    def wireframeMode(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    def filledMode(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    def setShaders(self, vertexShader, fragShader):
        if vertexShader is not None and fragShader is not None:
            self.active_shader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                 compileShader(fragShader, GL_FRAGMENT_SHADER))
        else:
            self.active_shader = None

    def render(self):
        glClearColor(0.2,0.2,0.2,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.active_shader)
        if self.active_shader:
            glUniformMatrix4fv(glGetUniformLocation(self.active_shader, "viewMatrix"),
                               1, GL_FALSE, glm.value_ptr(self.getViewMatrix()))

            glUniformMatrix4fv(glGetUniformLocation(self.active_shader, "projectionMatrix"),
                               1, GL_FALSE, glm.value_ptr(self.projectionMatrix))

            glUniform1f(glGetUniformLocation(self.active_shader, "tiempo"), self.tiempo)
            glUniform1f(glGetUniformLocation(self.active_shader, "valor"), self.valor)

            glUniform3f(glGetUniformLocation(self.active_shader, "pointLight"),
                        self.pointLight.x, self.pointLight.y, self.pointLight.z)

        for model in self.scene:
            if self.active_shader:
                glUniformMatrix4fv(glGetUniformLocation(self.active_shader, "modelMatrix"),
                                   1, GL_FALSE, glm.value_ptr(model.getModelMatrix()))

            model.renderInScene()