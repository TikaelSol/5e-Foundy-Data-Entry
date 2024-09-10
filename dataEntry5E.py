from regex import sub, IGNORECASE
from pyperclip import copy
from tkinter import Tk, Frame, Canvas, Text, Button, END, BooleanVar, Menu

deityFields = ("(Alignment|Siblings|Temples|Worshippers|Sacred Animal|Sacred Colors|Suggested Domains|Favored Weapon|"
               + "Divine Ability|Divine Skill|Key Edicts|Key Anathema)")
conditions = "(Blinded|Charmed|Deafened|Frightened|Grappled|Incapacitated|Invisible|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious)"
abilities = "(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
skills = ("(Acrobatics|Animal Handling|Arcana|Athletics|Deception|History|Insight|Intimidation|Investigation|Medicine|Nature|"
          + "Perception|Performance|Persuasion|Religion|Sleight of Hand|Stealth|Survival)")


def to_title(match_obj):
    if match_obj.group() is not None:
        return match_obj.group().title()


def handle_damage_rolls(string):
    string = sub(r" (\d)d(\d) (rounds|minutes|hours|days)", r" [[/r \1d\2 #\3]]{\1d\2 \3}", string)
    string = sub(r" (\d+) (\w*) damage", r" [[/r (\1)[\2]]]{\1 \2 damage}", string)
    string = sub(r"(\d+)d(\d+)\+(\d+) (\w*) damage", r"[[/r (\1d\2+\3)[\4]]]{\1d\2+\3 \4 damage}", string)
    string = sub(r"(\d+)d(\d+) (\w*) damage", r"[[/r \1d\2[\3]]]{\1d\2 \3 damage}", string)
    string = sub(r"(\d+)d(\d+) damage", r"[[/r \1d\2]] damage", string)
    string = sub(r"(\d+)d(\d+) (\w+)(\,|\.)", r"[[/r \1d\2 #\3]]{\1d\2 \3}\4", string)
    string = sub(r"(\d+)d(\d+)\.", r"[[/r \1d\2]].", string)

    return string


def handle_bullet_lists(string):
    string = sub(r"•", "</p><ul><li>", string, count=1)
    string = sub(r"•", "</li><li>", string)
    string = sub(r"•", "</li><li>", string)

    return string


def handle_headers(string):
    string = sub(r"\n([A-Z]\w+)\n", r"<h2>\1</h2><p>", string)
    string = sub(r"\n([A-Z]\w+) (\w+)\n", r"<h2>\1 \2</h2><p>", string)
    string = sub(r"\n([A-Z]\w+) (\w+) (\w+)\n", r"<h2>\1 \2 \3</h2><p>", string)

    string = sub(r"FEATURE: (\w+) (\w+) (\w+)", r"<p><strong>Feature:</strong> \1 \2 \3</p><p>", string)
    string = sub(r"FEATURE: (\w+) (\w+)", r"<p><strong>Feature:</strong> \1 \2</p><p>", string)
    string = sub(r"FEATURE: (\w+)", r"<p><strong>Feature:</strong> \1</p><p>", string)

    string = sub(r"<h2>(.*?)</h2>", to_title, string)
    string = sub(r"H2", r"h2", string)

    string = sub(r"\.<h2>", r".</p><h2>", string)

    string = sub(r"<h2>Sample (.*?)(n|N)ames</h2>", r"<h3>Sample \1\2ames</h3>", string)

    return string


def handle_proficiencies(string):
    string = sub(r"(Skill Proficiencies:|Tool Proficiencies:|Languages:|Equipment:)", r"</p><p><strong>\1</strong>", string)
    return string


def handle_bolded_subtitles(string):
    string = sub(r"\n([A-Z]\w+)\.", r"</p><p><strong>\1.</strong>", string)
    string = sub(r"\n([A-Z]\w+) ([A-Z]\w+)\.", r"</p><p><strong>\1 \2.</strong>", string)
    string = sub(r"\n([A-Z]\w+) ([A-Z]\w+) ([A-Z]\w+)\.", r"</p><p><strong>\1 \2 \3.</strong>", string)

    string = sub(r"<p><strong>(You Might)\.</strong>\.\.", r"<h2>\1...</h2>", string)
    string = sub(r"<p><strong>(Others Probably)\.</strong>\.\.", r"</ul><h2>\1...</h2><ul>", string)

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


def handle_deity(string):
    string = sub(r"%s\:" % deityFields, r"<p><strong>\1:</strong>", string)
    return string


def handle_secrets(string):
    string = sub(r"(.*?)/secret", r"<section class='secret'>\1</section>", string)
    return string


def handle_skills(string):
    # I'd be surprised if there isn't a way to do this in one line
    string = sub(r"(attempt a[n]?|make a[n]?) " + abilities + " \\(" + skills + "\\) check", lambda m: m.group(0).lower(), string)
    string = sub(r"(attempt a[n]?|make a[n]?) " + abilities.lower() + " \\((" + skills.lower() + "\\)) check", r"\1 [[/skill \4]] check", string)

    return string


def handle_saving_throws(string):
    # I'd be surprised if there isn't a way to do this in one line
    string = sub(r"DC (\d+) " + abilities + " saving throw", lambda m: m.group(0).lower(), string)
    string = sub(r"DC (\d+) " + abilities.lower() + " saving throw", r"[[/save \2 \1]]", string)

    string = sub(r"a[n]? " + abilities + " saving throw", lambda m: m.group(0).lower(), string)
    string = sub(r"(a[n]?) " + abilities.lower() + " saving throw", r"\1 [[/save \2]]", string)

    return string


def handle_actions(string):
    string = sub(r"(\+|\-)(\d+) to hit", r"<strong>\1\2 to hit</strong>", string)
    string = sub(r"reach (\d) ft", r"reach <strong>\1 ft</strong>", string)
    string = sub(r"Hit: (\d+) \((\d+)d(\d+) (\+|\-) (\d+)\) (\w+) damage", r"Hit: <strong>\1 (\2d\3 \4 \5) \6 damage</strong>", string)
    string = sub(r"Hit: (\d+) \((\d+)d(\d+)\) (\w+) damage", r"Hit: <strong>\1 (\2d\3) \6 damage</strong>", string)

    string = handle_secrets(string)
    return string


def handle_conditions(string):
    string = sub(conditions, r"&Reference[\1]", string, flags=IGNORECASE)
    # TODO: Handle leveled exhaustion condition
    return string


def handle_roll_tables(string):
    string = sub("Confusion table", r"@UUID[Compendium.dnd5e.tables.RollTable.LHEts1oDaDwcehuj]{Confusion} table", string)
    return string


def reformat(text, remove_non_ASCII = True, action_entry = True):
    string = "<p>" + text

    string = handle_headers(string)
    string = handle_bolded_subtitles(string)

    string = string.replace("\n", " ")
    string = string.replace("<p><p>", "<p>")
    string = string.replace(u'\xa0', u' ')
    string = string.replace("- ", "-")

    if remove_non_ASCII:
        string = string.replace(r"”", r'"').replace(r"“", r'"')
        string = string.replace("’", "'")

    if "d8 Personality Trait" in string:
        string = handle_background_tables(string)

    string = handle_deity(string)
    string = handle_bullet_lists(string)
    string = handle_proficiencies(string)
    string = handle_damage_rolls(string)
    string = handle_conditions(string)
    string = handle_roll_tables(string)

    if action_entry:
        string = handle_skills(string)
        string = handle_saving_throws(string)
        string = handle_actions(string)

    string = string.replace("<p></p>", "").replace("<p><p>", "<p>")
    string = string.replace(" <p>", "</p><p>")
    string = string.replace(" </p>", "</p>")
    string = string.replace(";</p>", "</p>")
    string = string.replace("<p> ", "<p>")

    copy(string)

    outputText.delete("1.0", END)
    outputText.insert(END, string)


###############################################################################
# Build with `pyinstaller --noconsole --icon="D20_icon.ico" --onefile dataEntry5E.py`
###############################################################################

def clearInput():
    inputText.delete("1.0", END)


Height = 700
Width = 800

root = Tk()

root.title("5E on Foundry VTT Data Entry v 1.0.5")

canvas = Canvas(root, height=Height, width=Width)
canvas.pack()

frame = Frame(root, bg='#80c0ff')
frame.place(relwidth=1, relheight=1)

inputText = Text(frame, bg='white')
inputText.place(rely=0.2, relwidth=0.49, relheight=0.8)

outputText = Text(frame, bg='white')
outputText.place(relx=0.51, rely=0.2, relwidth=0.49, relheight=0.8)

## Settings
###############################################################################
action_entry = BooleanVar(value = True)
remove_non_ASCII = BooleanVar(value = True)
# table_entry = BooleanVar(value = False)
# unused = BooleanVar(value = False)
###############################################################################


# Build settings menu
##############################################################################

menu = Menu(root)

settings_menu = Menu(menu)
settings_menu.add_checkbutton(label = "Entering Action Text", variable = action_entry)
settings_menu.add_checkbutton(label = "Replace non-standard characters", variable = remove_non_ASCII)
# settings_menu.add_checkbutton(label = "Entering Roll Tables", variable = table_entry)
# settings_menu.add_checkbutton(label = "", variable = unused)

menu.add_cascade(label = "Settings", menu = settings_menu)
root.config(menu = menu)

reformatButton = Button(root, text = "Reformat Text", command = lambda: reformat(inputText.get("1.0", "end-1c"), remove_non_ASCII.get(), action_entry.get()))
reformatButton.place(relx = 0.75, rely = 0, relwidth = 0.25, relheight = 0.2)

resetButton = Button(root, text = "Clear Input", command = lambda: clearInput())
resetButton.place(relx = 0, rely = 0, relwidth = 0.25, relheight = 0.2)

def main():
    root.mainloop()

if __name__ == "__main__":
    main()