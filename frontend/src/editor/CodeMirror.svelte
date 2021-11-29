<script lang="ts">
import { onMount } from 'svelte';
import { makeEditor } from './index';
let me: HTMLElement;
export const editor = makeEditor();
onMount(() => {
    me.appendChild(editor.view.dom);
});
</script>


<div bind:this={me}>

</div>


<style lang="scss">
div {
    --codemirror-active-line: #fbfbfb;
    --codemirror-gutter-color: #eeeeee;
    height: var(--codemirror-min-height);
    max-height: 100%;
    overflow-y: scroll;
}
</style>