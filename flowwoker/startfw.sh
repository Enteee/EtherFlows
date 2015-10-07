rm -rf eno*
./fworker.py eno2 &
./fworker.py eno3 &
./fworker.py eno4 &
wait
