import discord

import embed_formatters


def compare_embeds(expected: discord.Embed, real: discord.Embed) -> None:
    assert expected.title == real.title
    assert expected.color == real.color
    assert len(expected.fields) == len(real.fields)
    for a, b in zip(expected.fields, real.fields):
        assert a == b
    assert expected == real


def test_format_week_embed_1() -> None:
    real = embed_formatters.format_week_embed(1)
    expected = discord.Embed(title="Event Rotation Week 1", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Banette] ([M+5][MS][C-1][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Mew] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Litten] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Typhlosion] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Accelgor] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Roserade (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Deoxys (Attack Forme)] [[PSB] 50.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Decidueye] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Grubbin] (16.67%), [Charjabug] (10.00%), [Vikavolt] (3.33%), [Crabrawler] (16.67%), "
        "[Crabominable] (6.67%), [Caterpie] (16.67%), [Metapod] (10.00%), [Butterfree] (3.33%), "
        "[Yungoos] (13.33%), [Gumshoos] (3.33%) [[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Pinsir] [[PSB] 100.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Rotom (Fan Rotom)]"
        "[Rotom (Frost Rotom)]"
        "[Rotom (Heat Rotom)]"
        "[Rotom (Wash Rotom)]"
        "[Rotom (Mow Rotom)] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_2() -> None:
    real = embed_formatters.format_week_embed(2)
    expected = discord.Embed(title="Event Rotation Week 2", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Xerneas] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Ho-Oh] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Rowlet] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Meganium] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Amoonguss] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Emboar] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Regigigas] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Volcanion] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Tornadus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Druddigon][Pachirisu][Sigilyph][Tropius][Farfetch'd] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_3() -> None:
    real = embed_formatters.format_week_embed(3)
    expected = discord.Embed(title="Event Rotation Week 3", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Garchomp] ([MS][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Lugia] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Popplio] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Feraligatr] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Escavalier] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Hawlucha (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Nihilego] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Gible] (13.33%), [Gabite] (10.00%), [Garchomp] (3.33%), [Staryu] (13.33%), "
        "[Starmie] (6.67%), [Furfrou] (10.00%), [Manaphy (Winking)] (6.67%), "
        "[Phione] (6.67%), [Phione (Winking)] (3.33%), [Sandygast] (26.67%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Frillish (Female)] [[Heart] 100.0% / [Heart] 50.0% / [MSU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Spiritomb][Girafarig][Kecleon][Shuckle][Relicanth] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_4() -> None:
    real = embed_formatters.format_week_embed(4)
    expected = discord.Embed(title="Event Rotation Week 4", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Yveltal] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Celebi] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Wobbuffet (Male)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Regirock] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Golem] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Marowak (Alola Form)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Meloetta (Pirouette Forme)] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Latios] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Thundurus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Clefairy (Winking)]"
        "[Charmander (Winking)]"
        "[Squirtle (Winking)]"
        "[Bulbasaur (Winking)]"
        "[Jigglypuff (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_5() -> None:
    real = embed_formatters.format_week_embed(5)
    expected = discord.Embed(title="Event Rotation Week 5", color=0xFF0000)
    expected.add_field(
        inline=False, name="Competitive Stage", value="- [Mega Steelix] ([MS][DD][APU])"
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Kyogre] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Drifloon] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Regice] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Drifblim] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Muk (Alola Form)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Arceus] [[PSB] 50.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Krabby] (16.67%), [Kingler] (6.67%), [Shellder] (16.67%), [Cloyster] (6.67%), "
        "[Magikarp (Shiny)] (3.33%), [Gyarados (Shiny)] (3.33%), [Goldeen] (16.67%), [Seaking] (10.00%), "
        "[Aipom] (13.33%), [Ambipom] (6.67%) [[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Jellicent (Female)] [[Heart] 100.0% / [Heart] 50.0% / [LU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Seviper][Wynaut][Torkoal][Zangoose][Luvdisc] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_6() -> None:
    real = embed_formatters.format_week_embed(6)
    expected = discord.Embed(title="Event Rotation Week 6", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Genesect] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Groudon] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Cyndaquil (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Registeel] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Mimikyu] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Dhelmise] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Buzzwole] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Giratina (Altered Forme)] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Landorus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Maractus][Dunsparce][Qwilfish][Durant][Heatmor] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_7() -> None:
    real = embed_formatters.format_week_embed(7)
    expected = discord.Embed(title="Event Rotation Week 7", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Manectric] ([MS][C-1][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Dialga] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Chikorita (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Lycanroc] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Salazzle] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Toxapex] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Kyurem (White Kyurem)] [[PSB] 50.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Electrike] (13.33%), [Manectric] (6.67%), [Darumaka] (16.67%), [Darmanitan] (10.00%), "
        "[Pikachu (Winking)] (6.67%), [Raichu (Winking)] (6.67%), [Plusle] (13.33%), [Minun] (13.33%), "
        "[Diglett (Alola Form)] (10.00%), [Dugtrio (Alola Form)] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmog] [[PSB] 100.0% / [SBS] 25.0% / [EBL] 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Lunatone][Tyrogue][Castform][Mantyke][Solrock] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_8() -> None:
    real = embed_formatters.format_week_embed(8)
    expected = discord.Embed(title="Event Rotation Week 8", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Mewtwo (Shiny)] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Palkia] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Totodile (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Wailord] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Toucannon] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Wigglytuff (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Kyurem (Black Kyurem)] [[PSB] 50.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Latias] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmoem] [[PSB] 100.0% / [SBS] 25.0% / [RML] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Pikachu (Sleeping)]"
        "[Torchic (Winking)]"
        "[Treecko (Winking)]"
        "[Mudkip (Winking)]"
        "[Castform (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_9() -> None:
    real = embed_formatters.format_week_embed(9)
    expected = discord.Embed(title="Event Rotation Week 9", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Gyarados] ([MS][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Gyarados] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Passimian] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Minior] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Noivern] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Metagross (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Pheromosa] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Salandit] (20.00%), [Togedemaru] (6.67%), [Roggenrola] (16.67%), "
        "[Boldore] (10.00%), [Gigalith] (3.33%), [Rockruff] (6.67%), [Geodude (Alola Form)] (16.67%), "
        "[Graveler (Alola Form)] (10.00%), [Golem (Alola Form)] (3.33%), [Mareanie] (6.67%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Pinsir] [[PSB] 100.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Pom-Pom Style)]"
        "[Wishiwashi][Komala][Fomantis][Torracat] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_10() -> None:
    real = embed_formatters.format_week_embed(10)
    expected = discord.Embed(title="Event Rotation Week 10", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Tyranitar (Shiny)] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Shaymin (Sky Forme)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Oranguru] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Raichu (Alola Form)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Armaldo] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Mudsdale] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Ho-Oh (Shiny)] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Diancie] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Pikachu (Charizard Costume)] (16.67%), [Pikachu (Magikarp Costume)] (16.67%), "
        "[Pikachu (Gyarados Costume)] (16.67%), [Pikachu (Shiny Gyarados Costume)] (10.00%), "
        "[Pikachu (Lugia Costume)] (3.33%), [Pikachu (Ho-Oh Costume)] (3.33%), "
        "[Pikachu (Rayquaza Costume)] (3.33%), [Pikachu (Shiny Rayquaza Costume)] (3.33%), "
        "[Pikachu (Kimono Boy)] (13.33%), [Pikachu (Kimono Girl)] (13.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Tornadus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Pa'u Style)]"
        "[Grimer (Alola Form)]"
        "[Dewpider][Sandshrew (Alola Form)]"
        "[Brionne] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_11() -> None:
    real = embed_formatters.format_week_embed(11)
    expected = discord.Embed(title="Event Rotation Week 11", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Alakazam] ([M+5][C-1][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Manaphy] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Chimchar (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Talonflame] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Cradily] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Blissey (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Zygarde (Complete Forme)] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Abra] (13.33%), [Kadabra] (10.00%), [Alakazam] (3.33%), [Tauros] (13.33%), "
        "[Oddish] (20.00%), [Gloom] (10.00%), [Vileplume] (3.33%), [Bounsweet] (13.33%), "
        "[Steenee] (10.00%), [Tsareena] (3.33%) [[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Frillish (Female)] [[Heart] 100.0% / [Heart] 50.0% / [MSU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Baile Style)]"
        "[Pyukumuku][Oricorio (Sensu Style)]"
        "[Mudbray][Dartrix] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_12() -> None:
    real = embed_formatters.format_week_embed(12)
    expected = discord.Embed(title="Event Rotation Week 12", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Salamence] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Reshiram] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Turtwig (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Rhyperior] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Kingdra] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Togekiss (Winking)] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Xurkitree] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Darkrai] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Thundurus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Slurpuff (Winking)]"
        "[Audino (Winking)]"
        "[Togetic (Winking)]"
        "[Carbink (Winking)]"
        "[Swirlix (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_13() -> None:
    real = embed_formatters.format_week_embed(13)
    expected = discord.Embed(title="Event Rotation Week 13", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Pinsir] ([M+5][DD][MS][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Zekrom] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Piplup (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Omastar] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Breloom] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Charizard (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Tapu Koko] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Burmy (Trash Cloak)] (20.00%), [Wormadam (Trash Cloak)] (3.33%), "
        "[Pikachu (Angry)] (3.33%), [Deerling (Spring Form)] (20.00%), "
        "[Sawsbuck (Spring Form)] (10.00%), [Morelull] (16.67%), [Shiinotic] (6.67%), "
        "[Wimpod] (3.33%), [Venonat] (13.33%), [Venomoth] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Jellicent (Female)] [[Heart] 100.0% / [Heart] 50.0% / [LU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Rotom (Fan Rotom)]"
        "[Rotom (Frost Rotom)]"
        "[Rotom (Heat Rotom)]"
        "[Rotom (Wash Rotom)]"
        "[Rotom (Mow Rotom)] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_14() -> None:
    real = embed_formatters.format_week_embed(14)
    expected = discord.Embed(title="Event Rotation Week 14", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Rayquaza] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Keldeo (Ordinary Form)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Wobbuffet (Female)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Kabutops] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Slaking] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Azumarill (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Tapu Fini] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Kyurem] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Sunkern] (20.00%), [Sunflora] (3.33%), [Pikipek] (20.00%), [Trumbeak] (10.00%), "
        "[Lurantis] (3.33%), [Drampa] (3.33%), [Deerling (Summer Form)] (20.00%), "
        "[Sawsbuck (Summer Form)] (6.67%), [Stantler] (10.00%), [Pikachu (Dizzy)] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Landorus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Druddigon][Pachirisu][Sigilyph][Tropius][Farfetch'd] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_15() -> None:
    real = embed_formatters.format_week_embed(15)
    expected = discord.Embed(title="Event Rotation Week 15", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Camerupt] ([MS][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Cresselia] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Comfey] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Bellossom] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Exeggutor (Alola Form)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Kommo-o] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Celesteela] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Numel] (16.67%), [Camerupt] (3.33%), [Hippopotas (Female)] (16.67%), "
        "[Hippowdon (Female)] (3.33%), [Pidove] (20.00%), [Tranquill] (10.00%), "
        "[Unfezant (Male)] (6.67%), [Unfezant (Female)] (3.33%), [Jangmo-o] (13.33%), "
        "[Hakamo-o] (6.67%) [[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmog] [[PSB] 100.0% / [SBS] 25.0% / [EBL] 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Spiritomb][Girafarig][Kecleon][Shuckle][Relicanth] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_16() -> None:
    real = embed_formatters.format_week_embed(16)
    expected = discord.Embed(title="Event Rotation Week 16", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Luxray] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Zygarde (10% Forme)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Tepig (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Politoed] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Machamp] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Keldeo (Resolute Form)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Solgaleo] [[PSB] 25.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Zygarde (50% Forme)] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmoem] [[PSB] 100.0% / [SBS] 25.0% / [RML] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Clefairy (Winking)]"
        "[Charmander (Winking)]"
        "[Squirtle (Winking)]"
        "[Bulbasaur (Winking)]"
        "[Jigglypuff (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_17() -> None:
    real = embed_formatters.format_week_embed(17)
    expected = discord.Embed(title="Event Rotation Week 17", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Beedrill] ([MS][C-1][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Diancie (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Snivy (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Electivire] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Beedrill] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Bruxish] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Lunala] [[PSB] 25.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Pikachu (Original Cap)] (10.00%), [Pikachu (Hoenn Cap)] (10.00%), "
        "[Pikachu (Sinnoh Cap)] (10.00%), [Pikachu (Unova Cap)] (10.00%), "
        "[Pikachu (Kalos Cap)] (10.00%), [Pikachu (Alola Cap)] (10.00%), "
        "[Pikachu (Smiling)] (13.33%), [Pikachu (Happy)] (3.33%), [Pikachu (Fired Up)] (20.00%), "
        "[Pikachu (Surprised)] (3.33%) [[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Pinsir] [[PSB] 100.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Seviper][Wynaut][Torkoal][Zangoose][Luvdisc] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_18() -> None:
    real = embed_formatters.format_week_embed(18)
    expected = discord.Embed(title="Event Rotation Week 18", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Hydreigon] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Hoopa (Hoopa Confined)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Oshawott (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Magmortar] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Dusknoir] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Gengar (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Kartana] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Meloetta (Aria Forme)] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Meowth (Alola Form)] (16.67%), [Persian (Alola Form)] (6.67%), "
        "[Rattata (Alola Form)] (16.67%), [Raticate (Alola Form)] (6.67%), [Unown (N)] (10.00%), "
        "[Unown (I)] (10.00%), [Unown (C)] (10.00%), [Unown (E)] (10.00%), "
        "[Cherubi (Winking)] (10.00%), [Cherrim (Winking)] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Tornadus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Maractus][Dunsparce][Qwilfish][Durant][Heatmor] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_19() -> None:
    real = embed_formatters.format_week_embed(19)
    expected = discord.Embed(title="Event Rotation Week 19", color=0xFF0000)
    expected.add_field(
        inline=False, name="Competitive Stage", value="- [Mega Houndoom] ([DD][APU])"
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Tornadus (Therian Forme)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Delcatty (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Ninetales (Alola Form)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Golisopod] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Ribombee] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Tapu Bulu] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Pineco] (16.67%), [Forretress] (6.67%), [Ledyba] (13.33%), [Ledian] (6.67%), "
        "[Houndour] (13.33%), [Houndoom] (3.33%), [Noibat] (13.33%), [Hoothoot] (16.67%), "
        "[Noctowl] (6.67%), [Vivillon (Poké Ball Pattern)] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Frillish (Female)] [[Heart] 100.0% / [Heart] 50.0% / [MSU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Lunatone][Tyrogue][Castform][Mantyke][Solrock] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_20() -> None:
    real = embed_formatters.format_week_embed(20)
    expected = discord.Embed(title="Event Rotation Week 20", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Porygon-Z] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Thundurus (Therian Forme)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Stufful] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Hitmonlee] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Greninja (Ash-Greninja)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Bewear] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Tapu Lele] [[PSB] 25.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Giratina (Origin Forme)] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Thundurus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Pikachu (Sleeping)]"
        "[Torchic (Winking)]"
        "[Treecko (Winking)]"
        "[Mudkip (Winking)]"
        "[Castform (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_21() -> None:
    real = embed_formatters.format_week_embed(21)
    expected = discord.Embed(title="Event Rotation Week 21", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Gardevoir] ([MS][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Landorus (Therian Forme)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Fennekin (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Hitmonchan] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Araquanid] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Gardevoir (Shiny)] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Guzzlord] ([Coin] x20000)\n",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Sewaddle] (16.67%), [Swadloon] (10.00%), [Leavanny] (3.33%), "
        "[Cottonee (Winking)] (16.67%), [Whimsicott (Winking)] (6.67%), "
        "[Flabébé (Winking)] (13.33%), [Floette (Winking)] (6.67%), [Snubbull (Winking)] (6.67%), "
        "[Chansey (Winking)] (3.33%), [Cutiefly] (16.67%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Jellicent (Female)] [[Heart] 100.0% / [Heart] 50.0% / [LU] 12.5%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Pom-Pom Style)][Wishiwashi][Komala][Fomantis][Torracat] "
        "[[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_22() -> None:
    real = embed_formatters.format_week_embed(22)
    expected = discord.Embed(title="Event Rotation Week 22", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Goodra] [[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Uxie] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Chespin (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Type: Null] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Turtonator] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Carracosta] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Silvally] [[PSB] 50.0% / 25.0% / 6.25%] ([Heart] x2)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Magearna] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Landorus (Incarnate Forme)] [[PSB] 100.0% / [PSB] 12.5% / [MSU] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Pa'u Style)]"
        "[Grimer (Alola Form)]"
        "[Dewpider][Sandshrew (Alola Form)]"
        "[Brionne] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_23() -> None:
    real = embed_formatters.format_week_embed(23)
    expected = discord.Embed(title="Event Rotation Week 23", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Competitive Stage",
        value="- [Mega Charizard X] ([C-1][DD][APU])",
    )
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Mesprit] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Froakie (Winking)] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Infernape] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Hitmontop] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Granbull (Winking)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Marshadow] [[PSB] 25.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Incineroar] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Safari",
        value="- [Fletchling] (20.00%), [Fletchinder] (10.00%), [Zigzagoon] (16.67%), "
        "[Linoone] (6.67%), [Hoppip (Winking)] (16.67%), [Skiploom (Winking)] (10.00%), "
        "[Jumpluff (Winking)] (3.33%), [Vulpix (Alola Form)] (3.33%), "
        "[Snorunt (Winking)] (10.00%), [Glalie (Winking)] (3.33%) "
        "[[EBS] 25.0% / [EBM] 3.125% / [EBL] 1.5625%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmog] [[PSB] 100.0% / [SBS] 25.0% / [EBL] 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Oricorio (Baile Style)]"
        "[Pyukumuku][Oricorio (Sensu Style)]"
        "[Mudbray][Dartrix] [[Coin] x100 50.0% / [Coin] x300 12.5% / [Coin] x2000 3.125%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_24() -> None:
    real = embed_formatters.format_week_embed(24)
    expected = discord.Embed(title="Event Rotation Week 24", color=0xFF0000)
    expected.add_field(
        inline=False,
        name="Challenges",
        value="- [Hoopa (Hoopa Unbound)] "
        "[[PSB] 25.0% / [PSB] 25.0% / [RML] 1.5625%] ([Coin] x300)\n"
        "- [Azelf] [[PSB] 50.0% / 25.0% / 12.5%] ([Heart] x2)\n"
        "- [Carnivine] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Archeops] [[PSB] 25.0% / 25.0% / 12.5%]\n"
        "- [Sandslash (Alola Form)] [[PSB] 25.0% / 12.5% / 6.25%] ([Coin] x300)\n"
        "- [Palossand] [[PSB] 25.0% / 12.5% / 6.25%]\n"
        "- [Necrozma] [[PSB] 25.0% / 25.0% / 6.25%] ([Coin] x500)\n",
    )
    expected.add_field(
        inline=False,
        name="Escalation Battles",
        value="- [Primarina] [[PSB] 25.0% / 25.0% / 25.0%]",
    )
    expected.add_field(
        inline=False,
        name="One Chance a Day!",
        value="- [Cosmoem] [[PSB] 100.0% / [SBS] 25.0% / [RML] 6.25%]",
    )
    expected.add_field(
        inline=False,
        name="Daily",
        value="- [Slurpuff (Winking)]"
        "[Audino (Winking)]"
        "[Togetic (Winking)]"
        "[Carbink (Winking)]"
        "[Swirlix (Winking)] [[PSB] 50.0% / 25.0% / 12.5%]",
    )

    compare_embeds(expected, real)


def test_format_week_embed_fake_week_less() -> None:
    real = embed_formatters.format_week_embed(0)
    expected = discord.Embed(title="Event Rotation Week 0", color=0xFF0000)
    expected.add_field(inline=False, name="Challenges", value="")
    expected.add_field(inline=False, name="One Chance a Day!", value="")
    expected.add_field(inline=False, name="Daily", value="")

    compare_embeds(expected, real)


def test_format_week_embed_fake_week_more() -> None:
    real = embed_formatters.format_week_embed(25)
    expected = discord.Embed(title="Event Rotation Week 25", color=0xFF0000)
    expected.add_field(inline=False, name="Challenges", value="")
    expected.add_field(inline=False, name="One Chance a Day!", value="")
    expected.add_field(inline=False, name="Daily", value="")

    compare_embeds(expected, real)
