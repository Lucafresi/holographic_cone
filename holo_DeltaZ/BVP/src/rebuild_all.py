import os, sys, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def run(py):
    print(">>", py)
    subprocess.check_call([sys.executable, os.path.join(ROOT, "src", py)])
if __name__=="__main__":
    run("bvp_bounds.py")
    print("All BVP certificates rebuilt.")
