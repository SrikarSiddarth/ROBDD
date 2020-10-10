import numpy as np
import time
import cv2 as cv
import random

# robdd node data structure
class node():

	def __init__(self, v=None, z = None, o=None, i=None):
		# self.parent = []		# this data type may have more than one parent
		self.id = i			# id is not the same as value
		self.value = v		# value is the variable shown on the node
							# value is also used for classifying the nodes based on levels
		self.zero = z		# the child node if the value v is 0
		self.one = o		# the child node if the value v is 1



class robdd():

	def __init__(self):
		self.varList = []					# storing the list of variables in the order required to construct the robdd
		self.varCubeList = []				# cube list for the variables
		self.expression = []
		self.n = 0							# number of variables
		self.UT = [[],[]]					# unique table [[keys][nodes]]
		self.drawTable = [[],[]]			# draw table
		self.zero = node('0')
		self.zero.id = 'zero'
		self.one = node('1')
		self.one.id = 'one'
		self.robdd = None
		self.robddDepth = 0
		self.height = 1000
		self.width = 1000
		self.cirRad = 15
		self.offset = 20
		self.treeHeight = 80
		self.reducedVarList = []
		self.treeWidth = 30
		self.img = None

	def pOT(self,root,i):								# post order traverse
		if root:
			self.pOT(root.zero,i+1)
			self.pOT(root.one,i+1)
			if i>self.robddDepth:
				self.robddDepth = i
			print(root.value,end=" ")



	def pOT2(self,root,i):								# pre order traversal
		if root:
			# it is a terminal node 
			if root.value=='0' and root.id not in self.drawTable[0]:
					self.drawCircle([int(self.width*0.5)-5*self.treeWidth,self.height-self.offset],root)
					self.drawTable[0].append(root.id)
					self.drawTable[1].append([int(self.width*0.5)-5*self.treeWidth,self.height-self.offset])
			elif root.value=='1' and root.id not in self.drawTable[0]:
					self.drawCircle([int(self.width*0.5)+5*self.treeWidth,self.height-self.offset],root)
					self.drawTable[0].append(root.id)
					self.drawTable[1].append([int(self.width*0.5)+5*self.treeWidth,self.height-self.offset])

			# else:		
			# 	# it is not a terminal node
			# 	if root.zero.id in self.drawTable[0]:
			# 		# draw a blue line between this node


			self.pOT2(root.zero,i+1)	
			if i<self.robddDepth and root.value!='0' and root.value!='1':
				if root.id not in self.drawTable[0]:
					k = random.randint(self.offset,self.width-self.offset)
					self.drawCircle([k,self.offset+i*self.treeHeight],root)
					self.drawTable[0].append(root.id)
					self.drawTable[1].append([k,self.offset+i*self.treeHeight])
					# draw a blue line between this node and the zero-child node
					# print(self.drawTable)
					y = self.drawTable[1][self.drawTable[0].index(root.zero.id)]
					self.img = cv.line(self.img,(k,self.offset+i*self.treeHeight+self.cirRad),(y[0],y[1]-self.cirRad),(255,0,0),3)


			self.pOT2(root.one,i+1)
			if i<self.robddDepth and root.value!='0' and root.value!='1':
				# draw a red line between this node and the one-child node

				s = self.drawTable[1][self.drawTable[0].index(root.id)]
				y = self.drawTable[1][self.drawTable[0].index(root.one.id)]
				self.img = cv.line(self.img,(s[0],s[1]+self.cirRad),(y[0],y[1]-self.cirRad),(0,0,255),3)



	def draw(self):
		self.height = 2*self.offset + self.robddDepth*self.treeHeight
		self.img = np.ones((self.height,self.width,3),np.uint8)
		self.img.fill(255)
		self.pOT2(self.robdd,0)
		cv.imshow('a',self.img)
		cv.waitKey(0)
		cv.destroyAllWindows()

	def drawCircle(self, pos, n):
		self.img = cv.circle(self.img,(pos[0],pos[1]),self.cirRad,(100,200,200),2)
		font = cv.FONT_HERSHEY_SIMPLEX
		textsize = cv.getTextSize(n.value, font, 1, 2)[0]
		pos = (int(pos[0]-textsize[0]*0.25),int(pos[1]+textsize[1]*0.25))
		cv.putText(self.img,n.value,(pos[0],pos[1]), font, 0.5,(0,0,0),1,cv.LINE_AA)
		
	def drawLine(self,start,end,col):
		self.img = cv.line(self.img,start,end,col,5)



	def calc_cubelist(self, function):
		res = []
		for i in function:
			temp = []
			for j in range(self.n):
				index = i.find(self.varList[j])
				
				if index == len(i)-1:
					# so that the out of range error can be avoided
					temp.append(1)
					continue
				if index == -1:
					temp.append(0)
				elif i[index+1]=='\'':
					temp.append(2)
				else :
					temp.append(1)
			res.append(temp)
		return res

	def calc_cofactor(self,function,var):
		f = [r[:] for r in function]
		for i in range(self.n):
			if var[i]:
				j=0
				while j<len(f):
					if f[j][i]==var[i] or f[j][i]==0:
						f[j][i]=0
						j+=1
					else:
						f.remove(f[j])
		return f

	def calc_func(self,array):
		s = ''
		for i in range(len(array)):
			if all(array[i]==np.zeros(self.n)):
				s='1'
				break
			for j in range(self.n):
				if array[i][j]:
					s+=self.varList[j]
					if array[i][j]==2:
						s+='\''
			if i<len(array)-1:
				s+='+'
		if s=='':
			s='0'
		return s





	def input(self, s):
		self.e1 = s
		s = s.replace(" ","")
		s = s.split("+")

		self.varList = [w for w in input('Enter the order of variables : ')]
		self.n = len(self.varList)
		self.varCubeList = self.calc_cubelist(self.varList)
		self.expression = self.calc_cubelist(s)
		
		self.robdd = self.ITE(self.expression,0)

		self.pOT(self.robdd,0)
		print(' <-- Is the ROBDD in POST ORDER TRAVERSAL.')
		print('Press Enter to close. Thank You\nSrikar Siddarth\nThird Year Btech in Electronics and Communications Branch\nNITK')
		# print(self.robddDepth)
		self.draw()

	def ITE(self, function, i):
		v = np.copy(self.varCubeList[i])	# top variable
		fv_cube = self.calc_cofactor(function, v)
		# print('fv_cube '+str(fv_cube))
		fv = self.calc_func(fv_cube)
		v_bar = np.copy(self.varCubeList[i])
		for j in range(len(v_bar)):
			if v_bar[j]==1:
				v_bar[j]=2
		# print('v_bar '+str(v_bar))
		fv_bar_cube = self.calc_cofactor(function,v_bar)
		
		fv_bar = self.calc_func(fv_bar_cube)
		key = self.calc_func([v])+','+fv+','+fv_bar
		n = node(self.calc_func([v]))
		if fv=='0':
			n.one = self.zero
		elif fv=='1':
			n.one = self.one
		if fv_bar=='0':
			n.zero = self.zero
		elif fv_bar=='1':
			n.zero = self.one

		if n.one==None:
			n.one = self.ITE(fv_cube, i+1)
		if n.zero==None:
			n.zero = self.ITE(fv_bar_cube, i+1)

		n = self.searchUT(key,n)
		if n.one==n.zero:
			return n.one
		return n

	def searchUT(self, key, n):
		if key in self.UT[0]:
			return self.UT[1][self.UT[0].index(key)]
		else:
			n.id = len(self.UT[0])
			self.UT[0].append(key)
			self.UT[1].append(n)
			return n

	


if __name__ == '__main__':
	r = robdd()
	r.input(input('Enter the boolean expression in SOP form : '))