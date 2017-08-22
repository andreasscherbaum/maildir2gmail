#############
# You may want to change or omit the String "Old Mail" 
# You may want to change [Gmail]/Sent to your language, e.g. [Gmail]/Gesendet for german.
# GMail username and password here
# localuser for changing into local user directory
username=USER@DOMAIN.COM
passwd=PASSWORD
localuser=LOCALUSER
#
#############

shopt -s extglob
cd $localuser
for dir in Maildir/.!(mu-size|Sent|Spam|Trash|Drafts|Templates)

do
    echo "Directory:     $dir"
    label=${dir//\./\/}
    label=${label:9}
    echo "Converted to label: $label"
    python /root/maildir2gmail.py -f "Old Mail/$label" -u $username -p $passwd -n "$dir/new"
    python /root/maildir2gmail.py -f "Old Mail/$label" -u $username -p $passwd    "$dir/cur"

    echo
done

python /root/maildir2gmail.py -f "[Gmail]/Sent" -u $username -p $passwd   "Maildir/.Sent/cur"
python /root/maildir2gmail.py -f "INBOX" -u $username -p $passwd   "Maildir/cur"
python /root/maildir2gmail.py -f "INBOX" -u $username -p $passwd -n  "Maildir/new"
