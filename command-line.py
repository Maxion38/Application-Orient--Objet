import argparse
from programme import run_program

parser = argparse.ArgumentParser(description="A file organisation scrpit")
parser.add_argument("path", help="Path of the dir to sort", type=str)
parser.add_argument("-c", "--convention", help='Chose "us" for america (MM-DD-YY) or "int" for international ('
                                               'YY-MM-DD) format of the date', type=str)
parser.add_argument("-s", "--separator", help="Date separator char", type=str)
parser.add_argument("-o", "--order", help="Order of the date (dmy-mdy-ymd-...)", type=str)
parser.add_argument("-y", "--year", help="Years will be yyyy instead of yy", action="store_true")
parser.add_argument("-m", "--month", help="Months will be month name (ex: April) instead of mm", action="store_true")
args = parser.parse_args()


def format_dir_name(settings):
    # separator
    separator = "-"
    if settings.separator:
        separator = settings.separator

    # year
    year_form = "y"
    if settings.year:
        year_form = "Y"

    # month
    month_form = "m"
    if settings.month:
        month_form = "b"

    # default
    dir_format = f"%{year_form}{separator}%{month_form}{separator}%d"

    # convention
    if settings.convention == "us":
        dir_format = f"%{month_form}{separator}%d{separator}%{year_form}"

    # order "ymd"
    if settings.order:
        date_order = args.order
        if "d" in date_order and "m" in date_order and "y" in date_order and len(date_order) == 3:
            elem_list = {"d": "d", "m": month_form, "y": year_form}

            date_list = [elem_list[date_order[0]], elem_list[date_order[1]], elem_list[date_order[2]]]
            dir_format = f"%{date_list[0]}{separator}%{date_list[1]}{separator}%{date_list[2]}"

        else:
            print("Format incorect, il faut trois lettres d, m, y")


    return dir_format


dir_format_str = format_dir_name(args)
run_program(args.path, dir_format_str)


'''
    un paramètre pour choisir le séparateur (- .  _ etc)
        ex: -s -separator -> -
        raise error pour tous les caracteres illégaux (ex: .) 

    un paramètre pour choisir le format américain (MM-JJ-AA) ou internationnal (AA-MM-JJ)
        ex: -f -format -> america / internationnal 

    un paramètre pour choisir l'ordre des JJ MM AA
        ex: -o -order -> jma / amj / mja 

    un patamètre pour choisir si l'année est aa ou aaaa
        ex: -y -year -> yyyy / yy 
        
    Un paramètre pour choisir si le mois est mm ou par ex April (voir pour ajouter une lanngue ?)
        ex: -M -MONTH -> mm / April

    [avancé] un paramètre pour choisir comment trier les dossier. Par exemple, trier par jour, trier par mois, ou par 
    année
        ex: -s -sort -> day / month / year / day-month / month-year / day-month-year 

'''