while true; do 
    yaourt -Qua | wc -l > ~/.available_update_count
    sleep 6000
done
