import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import sveltePreprocess from 'svelte-preprocess';
import typescript from '@rollup/plugin-typescript';
import css from 'rollup-plugin-css-only';

const production = !process.env.ROLLUP_WATCH;

function serve() {
    let server;

    function toExit() {
        if (server) server.kill(0);
    }

    return {
        writeBundle() {
            if (server) return;
            server = require('child_process').spawn('npm', ['run', 'start', '--', '--dev'], {
                stdio: ['ignore', 'inherit', 'inherit'],
                shell: true
            });

            process.on('SIGTERM', toExit);
            process.on('exit', toExit);
        }
    };
}


const devPlugins = () => [
    serve(),  // Call `npm run start` once the bundle has been generated
    livereload("public"),  // Watch the `public` directory and refresh the browser
];


const productionPlugins = () => [
    terser(),  // minify the output
];


export default {
    input: 'src/main.ts',
    output: {
        sourcemap: true,
        format: 'iife',
        name: 'svelteApp',
        file: 'public/build/bundle.js',
        inlineDynamicImports: true,
    },
    plugins: [
        svelte({
            preprocess: sveltePreprocess({ sourceMap: !production }),
            compilerOptions: {
                // enable run-time checks when not in production
                dev: !production
            }
        }),
        // we'll extract any component CSS out into
        // a separate file - better for performance
        css({ output: 'bundle.css' }),

        resolve({
            browser: true,
            dedupe: ['svelte']
        }),

        typescript({
            sourceMap: !production,
            inlineSources: !production
        }),

        ...production ? productionPlugins() : devPlugins()
    ],
    watch: {
        clearScreen: false
    }
};
