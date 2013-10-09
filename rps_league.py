#!/usr/bin/env python3

from json import load

class Player:

    def __init__(self, name, stats):
        self.name = name
        self.wins = stats['wins']
        self.losses = stats['losses']
        self.draws = stats['draws']

    @property
    def played(self):
        return self.wins + self.losses + self.draws

    @property
    def points(self):
        return (self.wins*3) + self.draws


def get_league_list(players_fpath):
    with open(players_fpath, 'r') as f:
        players = load(f)
    plr_list = [Player(p, players[p]) for p in players]
    plr_list.sort(key=(lambda p: p.points), reverse=True)
    return plr_list

def get_html(plr_list, serv):
    lines = [
            '<html>',
            '<head><title>RockPaperScissors stats for {}</title></head>'.format(serv),
            '<body>'
            '<h2>Rock, Paper, Scissors stats for {}</h2>'.format(serv),
            '<table>',
            '<tr><td width="75">Rank</td><td width="150">Name</td><td width="75">Played</td><td width="75">Won</td><td width="75">Lost</td><td width="75">Drawn</td><td width="75">Points</td><td width="75">PPG</td></tr>',
            ]
    for r, p in enumerate(plr_list):
        lines.append(
                '<tr><td width="75">{}</td><td width="150">{}</td><td width="75">{}</td><td width="75">{}</td><td width="75">{}</td><td width="75">{}</td><td width="75">{}</td><td width="75">{}</td></tr>'.format(
                    r+1,
                    p.name,
                    p.played,
                    p.wins,
                    p.losses,
                    p.draws,
                    p.points,
                    round(p.points/p.played, 2)
                    )
                )
    lines.append('</table>')
    lines.append('</body>')
    lines.append('</html>')
    return lines

def main(infile, outfile, serv):
    plr_list = get_league_list(infile)
    html = get_html(plr_list, serv)
    with open(outfile, 'w') as f:
        f.writelines(html)

if __name__ == '__main__':
    # files and server name are hardcoded out of laziness
    in_out_serv = (
            (
                '/home/bunburya/.bunbot/rps/irc.freenode.net/players',
                '/home/bunburya/webspace/rps/freenode.html',
                'irc.freenode.net'
                ),
            (
                '/home/bunburya/.bunbot/rps/irc.netsoc.tcd.ie/players',
                '/home/bunburya/webspace/rps/intersocs.html',
                'intersocs'
                )
            )


    for infile, outfile, serv in in_out_serv:
        main(infile, outfile, serv)
