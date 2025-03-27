from simnibs import sim_struct, run_simnibs
# 进行tdcs刺激
# Initalize a session
s = sim_struct.SESSION()
# 包含head mesh的文件夹
s.subpath = 'D:\\moni\\m2m_Sub043'
# 输出文件夹
s.pathfem = f'D:\\moni\\m2m_Sub043\\test_tdcs'
# 初始化 tDCS 模拟
tdcslist = s.add_tdcslist()

tdcslist.currents = [1e-2,-1e-2,1e-2, -1e-2]

c1 = tdcslist.add_electrode()
c1.channelnr = 1
c1.dimensions = [15, 15]
c1.shape = 'ellipse'
c1.thickness = 5
c1.centre = 'F8'

c2 = tdcslist.add_electrode()
c2.channelnr = 2
c2.dimensions = [15, 15]
c2.shape = 'ellipse'
c2.thickness = 5
c2.centre = 'Fz'

c3 = tdcslist.add_electrode()
c3.channelnr = 3
c3.dimensions = [15, 15]
c3.shape = 'ellipse'
c3.thickness = 5
c3.centre = 'T8'

c4 = tdcslist.add_electrode()
c4.channelnr = 4
c4.dimensions = [15, 15]
c4.shape = 'ellipse'
c4.thickness = 5
c4.centre = 'T7'

s.open_in_gmsh = False

run_simnibs(s)



