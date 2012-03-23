#!/usr/bin/perl -w
#
# imgshack: Upload image files to imageshack.us.
#
# TODO: Add swf support.
#

use strict;

if (($#ARGV == -1) || ($ARGV[0] =~ /--help|-h/i )) {
    print <<HELP;
imgshack: Upload image files to imageshack.us.
Usage:
    imgshack [OPTION]... [FILE]...

Options:
    -h, --help      show this message.

Supported file types:
    jpg, jpeg, png, gif, bmp, tif, tiff.
HELP
    exit 0;
};

require LWP::UserAgent;

# my $type = qq[jpg|jpeg|png|gif|bmp|tif|tiff|swf] ;
my $type = qq[jpg|jpeg|png|gif|bmp|tif|tiff] ;
my $ua = LWP::UserAgent -> new;
$ua -> env_proxy;

foreach my $filename(@ARGV) {
    if (!(-r $filename && -f $filename)) { print STDERR "Fail: $filename: File dosen't exist or is not readable.\n"; next;};
    if (!($filename =~ m/\.($type)$/i)) { print STDERR "Fail: $filename: File type is not supported.\n"; next;};

    my $reply = $ua -> post( 'http://load.imageshack.us/' , 
        Content_Type => 'form-data',
        Content      => [ fileupload => ["$filename"] ]
    );
    if ($reply -> is_success ) {
        my $content = $reply -> content ;
        $content =~ s/\s+//g;
        if ($content =~ m'"([^"]+)"/></td><td[^>]*>Directlinktoimage'i) {
            print "$1\n";
        } else {
            print STDERR "Fail $filename: Could not get back the URL of the image.\n";
        }
    } else { 
        print STDERR "Fail $filename: ".$reply -> status_line ."\n";
    };
};
