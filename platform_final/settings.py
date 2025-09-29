# Stage 1 - Original level
stage_1 = [
	'                                                                  ',
	'                                                                  ',
	'                t  t            E                                 ',
	'        X     XXXXXXXXXs                   XX   X                 ',
	' tXXXt  E  XX     E   XX      E         XXXX tt XX      E          ',
	' XX XX                                      XXXXX                 ',
	'          Xt    t           t  t   X     E                     G',
	'        XXXXXX  XXXXs    XXXXXXXXXXX  XX              tt t    XXXX',
	' P   XX  X XX X  X XXXt     X XX  XX  XXX  XXXXXXXXs  XXXXXX      ',
	'XXXXXXX  X  X X  X  XXXXXXXXX XX  XX  XXX  XX XX XXXXXXX  X       ',
]

# Stage 2 - More challenging with different layout (goal properly positioned)
stage_2 = [
	'                                                                  ',
	'                                                                  ',
	'                    t    t                                        ',
	'           XXXX      E       XXXX                                ',
	'      tXXX     XX          XX     XXXt                           ',
	'     XX     E     XX      XX     E     XX        E                ',
	'  t      t    t      XXXX      t    t      t                     ',
	' XXXX  XXXXXXXXXX  XXXXXXXX  XXXXXXXXXX  XXXX    G               ',
	' P  XX  X      XX  X      XX  X      XX  XX  X   X               ',
	'XXXXXX  XXXXXXXX  XXXXXXXX  XXXXXXXX  XXXXXX    X               ',
]

# Stage 3 - Precision jumping challenge
stage_3 = [
	'                                                                  ',
	'                                                                  ',
	'  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  ',
	'                                                                  ',
	'                                                                  ',
	'                                                                  ',
	'                                                                  ',
	'  X    X    X    X    X    X    X    X    X    X    X    X    G  ',
	' P                                                              X  ',
	'XXXX  XXXX  XXXX  XXXX  XXXX  XXXX  XXXX  XXXX  XXXX  XXXX  XXXX ',
]

# Stage 4 - Boss stage (20 tiles wide to fit screen + invisible walls)
stage_4 = [
	'                    ',
	'                    ',
	'                    ',
	'                    ',
	'                    ',
	'                    ',
	'                    ',
	'XXX              XXX',
	'                    ',
	'XXXXXXXXXXXXXXXXXXXX',
]

# All stages
stages = [stage_1, stage_2, stage_3, stage_4]

# Current stage (will be managed by game)
world_map = stage_1  # Default to stage 1

tile_size = 50
WIDTH, HEIGHT = 1000, len(stage_1) * tile_size