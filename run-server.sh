#!/bin/sh
PORT=${PORT:-5000}
storage="${STORAGE:-filesystem}"
echo $storage
db_class=appr.models.kv.$storage.db:ApprDB
blob_class=appr.models.kv.$storage.blob:Blob
echo $db_class
DATABASE_URL="$HOME/.appr/packages" APPR_DB_CLASS=$db_class APPR_BLOB_CLASS=$blob_class gunicorn appr.api.wsgi:app -b :$PORT --timeout 120 -w 4 #--reload
