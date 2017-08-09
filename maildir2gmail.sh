username=USER@DOMAIN.COM
passwd=PASSWORD

shopt -s extglob
for dir in Maildir/.!(mu-size|Sent|Spam|Trash|Drafts)

do
    echo "Directory:     $dir"
        label=${dir//\./\/}
        label=${label:9}
    echo "Converted to label: $label"
    python /root/maildir2gmail.py -f "Alte Mails/$label" -u $username -p $passwd -n "$dir/new"
    python /root/maildir2gmail.py -f "Alte Mails/$label" -u $username -p $passwd    "$dir/cur"

    echo
done

python /root/maildir2gmail.py -f "[Gmail]/Gesendet" -u $username -p $passwd   "Maildir/.Sent/cur"
python /root/maildir2gmail.py -f "INBOX" -u $username -p $passwd   "Maildir/cur"
python /root/maildir2gmail.py -f "INBOX" -u $username -p $passwd -n  "Maildir/new"
