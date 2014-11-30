# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# algorithm tuning
N_QUANTIZED = 25             # start with an adaptive palette of this size
MIN_DISTANCE = 10.0          # min distance to consider two colors different
MIN_PROMINENCE = 0.05        # ignore if less than this proportion of image
MIN_SATURATION = 0.01        # ignore if not saturated enough
MAX_COLORS = 4               # keep only this many colors
BACKGROUND_PROMINENCE = 0.4  # level of prominence indicating a bg color

# multiprocessing parameters
N_PROCESSES = 1
BLOCK_SIZE = 10
SENTINEL = 'no more to process'
