import os

start_path = "models/snake_ppo_gen_"
k=0
for i in range(600, 150000, 300):
    if i%5000 != 0:
        dlt_path = start_path + str(i) + ".pth"
        k+=1
        if os.path.exists(dlt_path):
            os.remove(dlt_path)