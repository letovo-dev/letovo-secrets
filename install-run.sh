# to be continued...

current_ip=$(curl -s http://ipv4.icanhazip.com)

echo "Current public IPv4: $current_ip"

export CURRENT_IP=$current_ip
