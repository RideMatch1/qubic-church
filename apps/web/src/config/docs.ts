/**
 * Documentation configuration for the Bitcoin-Qubic Bridge Research
 * Structured following IMRAD academic format:
 * Introduction, Methods, Results, and Discussion
 */

import type { DocsConfig } from '@/lib/opendocs/types/docs'

export const docsConfig: DocsConfig = {
  mainNav: [
    {
      href: '/docs',

      title: {
        en: 'Research',
        pt: 'Pesquisa',
      },
    },
  ],

  sidebarNav: [
    {
      title: {
        en: 'Introduction',
        pt: 'Introducao',
      },

      items: [
        {
          href: '/docs',

          title: {
            en: 'Overview',
            pt: 'Visao Geral',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/02-background',

          title: {
            en: 'Background',
            pt: 'Contexto',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/03-motivation',

          title: {
            en: 'Motivation',
            pt: 'Motivacao',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/04-objectives',

          title: {
            en: 'Objectives',
            pt: 'Objetivos',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Methods',
        pt: 'Metodos',
      },

      items: [
        {
          href: '/docs/02-methods/01-methodology',

          title: {
            en: 'Methodology',
            pt: 'Metodologia',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/02-tools',

          title: {
            en: 'Tools',
            pt: 'Ferramentas',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/03-verification',

          title: {
            en: 'Verification',
            pt: 'Verificacao',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/04-analysis-framework',

          title: {
            en: 'Analysis Framework',
            pt: 'Framework de Analise',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/05-statistical-rigor',

          title: {
            en: 'Statistical Rigor',
            pt: 'Rigor Estatistico',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Results',
        pt: 'Resultados',
      },

      items: [
        {
          href: '/docs/03-results/01-bitcoin-bridge',

          title: {
            en: 'The Bitcoin Bridge',
            pt: 'A Ponte Bitcoin',
          },

          items: [],
        },

        {
          href: '/docs/03-results/02-formula-discovery',

          title: {
            en: 'Formula Discovery',
            pt: 'Descoberta da Formula',
          },

          items: [],
        },

        {
          href: '/docs/03-results/03-jinn-architecture',

          title: {
            en: 'JINN Architecture',
            pt: 'Arquitetura JINN',
          },

          items: [],
        },

        {
          href: '/docs/03-results/04-arb-oracle',

          title: {
            en: 'ARB Oracle',
            pt: 'Oraculo ARB',
          },

          items: [],
        },

        {
          href: '/docs/03-results/05-time-lock',

          title: {
            en: 'Time-Lock Mechanism',
            pt: 'Mecanismo Time-Lock',
          },

          items: [],
        },

        {
          href: '/docs/03-results/06-additional-findings',

          title: {
            en: 'Additional Findings',
            pt: 'Descobertas Adicionais',
          },

          items: [],
        },

        {
          href: '/docs/03-results/07-lost-knowledge-recovery',

          title: {
            en: 'Lost Knowledge Recovery',
            pt: 'Recuperacao de Conhecimento',
          },

          items: [],
        },

        {
          href: '/docs/03-results/08-unified-theory',

          title: {
            en: 'The Unified Theory',
            pt: 'A Teoria Unificada',
          },

          items: [],
        },

        {
          href: '/docs/03-results/09-identity-protocols',

          title: {
            en: 'Identity Protocols',
            pt: 'Protocolos de Identidade',
          },

          items: [],
        },

        {
          href: '/docs/03-results/10-paracosm-blueprint',

          title: {
            en: 'Paracosm Blueprint',
            pt: 'Blueprint do Paracosm',
          },

          items: [],
        },

        {
          href: '/docs/03-results/11-timeline-prophecy',

          title: {
            en: 'Timeline Prophecy',
            pt: 'Profecia do Cronograma',
          },

          items: [],
        },

        {
          href: '/docs/03-results/12-discord-archaeology',

          title: {
            en: 'Discord Archaeology',
            pt: 'Arqueologia do Discord',
          },

          items: [],
        },

        {
          href: '/docs/03-results/13-mathematical-proofs',

          title: {
            en: 'Mathematical Proofs',
            pt: 'Provas Matematicas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/14-glossary',

          title: {
            en: 'Glossary',
            pt: 'Glossario',
          },

          items: [],
        },

        {
          href: '/docs/03-results/15-forgotten-evidence',

          title: {
            en: 'Forgotten Evidence',
            pt: 'Evidencias Esquecidas',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Discussion',
        pt: 'Discussao',
      },

      items: [
        {
          href: '/docs/04-discussion/01-implications',

          title: {
            en: 'Implications',
            pt: 'Implicacoes',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/02-significance',

          title: {
            en: 'Significance',
            pt: 'Significancia',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/03-limitations',

          title: {
            en: 'Limitations',
            pt: 'Limitacoes',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/04-future-work',

          title: {
            en: 'Future Work',
            pt: 'Trabalhos Futuros',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Appendices',
        pt: 'Apendices',
      },

      items: [
        {
          href: '/docs/05-appendices/01-raw-data',

          title: {
            en: 'Raw Data Tables',
            pt: 'Tabelas de Dados',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/02-source-index',

          title: {
            en: 'Source File Index',
            pt: 'Indice de Arquivos',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/03-scripts',

          title: {
            en: 'Reproduction Scripts',
            pt: 'Scripts de Reproducao',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/04-discord-archive',

          title: {
            en: 'Discord Message Archive',
            pt: 'Arquivo de Mensagens',
          },

          items: [],
        },
      ],
    },
  ],
} as const
