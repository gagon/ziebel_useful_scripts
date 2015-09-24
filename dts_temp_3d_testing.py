from mayavi import mlab

black = (0,0,0)
white = (1,1,1)
mlab.figure(bgcolor=black)
mlab.plot3d([0, 1000], [0, 0], [0, 0], color=white, tube_radius=10.)
mlab.plot3d([0, 0], [0, 1500], [0, 0], color=white, tube_radius=10.)
mlab.plot3d([0, 0], [0, 0], [0, 1500], color=white, tube_radius=10.)
mlab.text3d(1050, -50, +50, 'X', color=white, scale=100.)
mlab.text3d(0, 1550, +50, 'Y', color=white, scale=100.)
mlab.text3d(0, -50, 1550, 'Z', color=white, scale=100.)
