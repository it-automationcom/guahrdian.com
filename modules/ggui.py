#{{{import
import sys
#}}}
#{{{class gui
class web:
    def __init__ (self,name):
        self.name="gui"
    def display(self):
        print("<script>")
        with open('includes/gui/js', 'r') as i:
            print(i.read())
        i.close
        print("</script>")
    def write(self):
        orig_stdout=sys.stdout
        f=open('/var/www/html/cache/gu.js','w')
        sys.stdout=f
        with open('includes/gui/js', 'r') as i:
            print(i.read())
        i.close
        f.close()
#}}}
# vim:foldmethod=marker:foldlevel=0

