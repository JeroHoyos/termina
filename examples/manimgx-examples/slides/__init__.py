from manim import FadeOut

from . import (
    bifurcation_mandelbrot,
    catenoid_helicoid,
    cherenkov_cone,
    circle_area,
    clifford_torus,
    colliding_blocks,
    complex_maps,
    derivative,
    dla_coral,
    euler_identity,
    fourier_pi,
    galton_board,
    harmonic_drive,
    heavy_top,
    hilbert_curve,
    hopf_fibration,
    kaleidoscope_sphere,
    kuramoto_fireflies,
    lagrange_points,
    life_spacetime,
    linear_maps,
    lorenz_attractor,
    lozenge_cubes,
    menger_slice,
    miura_ori,
    neural_untangle,
    phased_array,
    prime_spirals,
    pythagoras,
    quadratic_formula,
    riemann_sums,
    riemann_surfaces,
    rupert_cube,
    score_diffusion,
    sphere_packing,
    sugihara_cylinder,
    surface_plots,
    taylor_poles,
    taylor_series,
    tennis_racket,
    times_tables,
    title,
    traffic_helix,
    turing_torus,
    unit_circle,
    van_allen,
    voronoi_cones,
    vortex_rings,
    wave_packet,
)


class SlideBase:
    def start_slide(self):
        """Before each slide, whatever the previous one left fades out."""
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)


def _slide(build):
    def method(self):
        self.start_slide()
        build(self)

    return method


class TalkSlides:
    slide_title = _slide(title.build)
    slide_quadratic_formula = _slide(quadratic_formula.build)
    slide_pythagoras = _slide(pythagoras.build)
    slide_circle_area = _slide(circle_area.build)
    slide_euler_identity = _slide(euler_identity.build)
    slide_derivative = _slide(derivative.build)
    slide_riemann_sums = _slide(riemann_sums.build)
    slide_taylor_series = _slide(taylor_series.build)
    slide_unit_circle = _slide(unit_circle.build)
    slide_linear_maps = _slide(linear_maps.build)
    slide_complex_maps = _slide(complex_maps.build)
    slide_surface_plots = _slide(surface_plots.build)
    slide_fourier_pi = _slide(fourier_pi.build)
    slide_times_tables = _slide(times_tables.build)
    slide_colliding_blocks = _slide(colliding_blocks.build)
    slide_prime_spirals = _slide(prime_spirals.build)
    slide_hilbert_curve = _slide(hilbert_curve.build)
    slide_galton_board = _slide(galton_board.build)
    slide_lorenz_attractor = _slide(lorenz_attractor.build)
    slide_hopf_fibration = _slide(hopf_fibration.build)
    slide_clifford_torus = _slide(clifford_torus.build)
    slide_catenoid_helicoid = _slide(catenoid_helicoid.build)
    slide_kaleidoscope_sphere = _slide(kaleidoscope_sphere.build)
    slide_menger_slice = _slide(menger_slice.build)
    slide_lozenge_cubes = _slide(lozenge_cubes.build)
    slide_riemann_surfaces = _slide(riemann_surfaces.build)
    slide_rupert_cube = _slide(rupert_cube.build)
    slide_taylor_poles = _slide(taylor_poles.build)
    slide_voronoi_cones = _slide(voronoi_cones.build)
    slide_bifurcation_mandelbrot = _slide(bifurcation_mandelbrot.build)
    slide_sugihara_cylinder = _slide(sugihara_cylinder.build)
    slide_sphere_packing = _slide(sphere_packing.build)
    slide_heavy_top = _slide(heavy_top.build)
    slide_tennis_racket = _slide(tennis_racket.build)
    slide_lagrange_points = _slide(lagrange_points.build)
    slide_van_allen = _slide(van_allen.build)
    slide_vortex_rings = _slide(vortex_rings.build)
    slide_wave_packet = _slide(wave_packet.build)
    slide_cherenkov_cone = _slide(cherenkov_cone.build)
    slide_turing_torus = _slide(turing_torus.build)
    slide_kuramoto_fireflies = _slide(kuramoto_fireflies.build)
    slide_dla_coral = _slide(dla_coral.build)
    slide_phased_array = _slide(phased_array.build)
    slide_miura_ori = _slide(miura_ori.build)
    slide_harmonic_drive = _slide(harmonic_drive.build)
    slide_traffic_helix = _slide(traffic_helix.build)
    slide_score_diffusion = _slide(score_diffusion.build)
    slide_neural_untangle = _slide(neural_untangle.build)
    slide_life_spacetime = _slide(life_spacetime.build)
