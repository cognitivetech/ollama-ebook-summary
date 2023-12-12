cat q.json | while read line
do
  echo $line | jq .
  curl -d "$line" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq .
  sleep 10
done