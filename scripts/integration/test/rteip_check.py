import rtde_receive
rtde_r = rtde_receive.RTDEReceiveInterface("10.146.97.7")
print(rtde_r.getActualTCPPose())  