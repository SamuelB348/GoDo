import cProfile
import pstats


def main():

    ##########################
    # DODO
    ##########################

    ##########################
    # GOPHER
    ##########################
    pass


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
