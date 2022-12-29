from regex import sub
from pyperclip import copy
from tkinter import Tk, Frame, Canvas, Text, Button, END

def to_title(match_obj):
    if match_obj.group() is not None:
        return match_obj.group().title()

def handle_damage_rolls(string):
    string = sub(r" (\d)d(\d) (rounds|minutes|hours|days)", r" [[/r \1d\2 #\3]]{\1d\2 \3}", string)
    string = sub(r" (\d+) (\w*) damage", r" [[/r (\1)[\2]]]{\1 \2 damage}", string)
    string = sub(r"(\d+)d(\d+)\+(\d+) (\w*) damage", r"[[/r (\1d\2+\3)[\4]]]{\1d\2+\3 \4 damage}", string)
    string = sub(r"(\d+)d(\d+) (\w*) damage", r"[[/r \1d\2[\3]]]{\1d\2 \3 damage", string)
    string = sub(r"(\d+)d(\d+) damage", r"[[/r \1d\2]]{\1d\2 damage", string)
    string = sub(r"(\d+)d(\d+) (\w+)(\,|\.)", r"[[/r \1d\2 #\3]]{\1d\2 \3}\4", string)
    string = sub(r"(\d+)d(\d+)\.", r"[[/r \1d\2]].", string)
    
    return string

def handle_bullet_lists(string):
    string = sub(r"•", "<ul><li>", string, count=1)
    string = sub(r"•", "</li><li>", string)
    string = sub(r"•", "</li><li>", string)
    
    return string

def handle_headers(string):
    string = sub(r"\n([A-Z]\w+)\n", r"<h2>\1</h2>", string)
    string = sub(r"\n([A-Z]\w+) (\w+)\n", r"<h2>\1 \2</h2>", string)
    string = sub(r"\n([A-Z]\w+) (\w+) (\w+)\n", r"<h2>\1 \2 \3</h2>", string)
    
    string = sub(r"FEATURE: (\w+) (\w+) (\w+)", r"<p><strong>Feature:</strong> \1 \2 \3</p>", string)
    string = sub(r"FEATURE: (\w+) (\w+)", r"<p><strong>Feature:</strong> \1 \2</p>", string)
    string = sub(r"FEATURE: (\w+)", r"<p><strong>Feature:</strong> \1</p>", string)
    
    string = sub(r"<h2>(.*?)</h2>", to_title, string)
    string = sub(r"H2", r"h2", string)
    
    string = sub(r"\.<h2>", r".</p><h2>", string)
    
    return string

def handle_proficiencies(string):
    string = sub(r"(Skill Proficiencies:|Tool Proficiencies:|Languages:|Equipment:)", r"</p><p><strong>\1</strong>", string)
    
    return string

def handle_bolded_subtitles(string):
    string = sub(r"\n([A-Z]\w+)\.", r"</p><p><strong>\1.</strong>", string)
    string = sub(r"\n([A-Z]\w+) ([A-Z]\w+)\.", r"</p><p><strong>\1 \2.</strong>", string)
    string = sub(r"\n([A-Z]\w+) ([A-Z]\w+) ([A-Z]\w+)\.", r"</p><p><strong>\1 \2 \3.</strong>", string)
    
    return string

def handle_background_tables(string):
    string = sub(r"d8 Personality Trait", r"<table><thead><tr><th>d8</th><th>Personality Trait</th></tr></thead><tbody>", string)
    string = sub(r"d6 Ideal", r"</table><table><thead><tr><th>d6</th><th>Ideal</th></tr></thead><tbody>", string)
    string = sub(r"d6 Bond", r"</table><table><thead><tr><th>d6</th><th>Bond</th></tr></thead><tbody>", string)
    string = sub(r"d6 Flaw", r"</table><table><thead><tr><th>d6</th><th>Flaw</th></tr></thead><tbody>", string)
    
    string = sub(r" (\d) (.*?) (\d)", r"<tr><td>\1</td><td>\2</td></tr> \3", string)
    string = sub(r"</tr> (\d)", r"</tr><tr><td>\1</td><td>", string)
    string = sub(r"(^>)<tr>", r"\1<\td><\tr><tr>", string)
    string = sub(r"(\d)</td><td>(\w+)\.", r"\1</td><td><strong>\2.</strong>", string)
    string = sub(r"(\d)</td><td>(\w+) (\w+)\.", r"\1</td><td><strong>\2 \3.</strong>", string)
    string = sub(r"(\d)</td><td> (\w+)\.", r"\1</td><td><strong>\2.</strong>", string)
    string = sub(r"(\d)</td><td> (\w+) (\w+)\.", r"\1</td><td><strong>\2 \3.</strong>", string)
    string = sub(r" </table>", r"</td></tr></tbody></table>", string)
    
    string = string + "</td></tr></tbody></table>"
    string = sub(r"</p></td>", r"</td>", string)
    
    return string

def reformat(text):
    string = "<p>" + text + "</p>"    
    
    string = handle_headers(string)
    string = handle_bolded_subtitles(string)
    
    string = string.replace("\n", " ")
    string = string.replace("<p><p>", "<p>")
    string = string.replace(r"”", r'"').replace(r"“", r'"')
    string = string.replace("’", "'")
    string = string.replace("- ", "-")

    if "d8 Personality Trait" in string:
        string = handle_background_tables(string)

    string = handle_bullet_lists(string)

    string = handle_proficiencies(string)

    string = handle_damage_rolls(string)
    
    string = string.replace("<p></p>","").replace("<p><p>","<p>")
    string = string.replace(" <p>","</p><p>")
    string = string.replace(" </p>", "</p>")
    string = string.replace(";</p>","</p>")
    string = string.replace("<p> ","<p>")
    
    copy(string)

    outputText.delete("1.0", END)
    outputText.insert(END, string)
    
###############################################################################
# Build with `pyinstaller --noconsole --icon="D20_icon.ico" --onefile dataEntry.py`
###############################################################################

def clearInput():
    inputText.delete("1.0", END)

Height = 700
Width = 800

root = Tk()

root.title("5E on Foundry VTT Data Entry v 1.0.1")

canvas = Canvas(root, height = Height, width = Width)
canvas.pack()

frame = Frame(root, bg = '#80c0ff')
frame.place(relwidth = 1, relheight = 1)

inputText = Text(frame, bg = 'white')
inputText.place(rely = 0.2, relwidth = 0.49, relheight = 0.8)

outputText = Text(frame, bg = 'white')
outputText.place(relx = 0.51, rely = 0.2, relwidth = 0.49, relheight = 0.8)


reformatButton = Button(root, text="Reformat Text", command = lambda: reformat(inputText.get("1.0", "end-1c")))
reformatButton.place(relx = 0.75, rely= 0, relwidth = 0.25, relheight = 0.2)

resetButton = Button(root, text="Clear Input", command = lambda: clearInput())
resetButton.place(relx = 0, rely= 0, relwidth = 0.25, relheight = 0.2)

def main():
    root.mainloop()

if __name__ == "__main__":
    main()